import atexit
import os
import time
import pandas
import json

import flask
from flask import request
from flask import send_from_directory
from flask import Flask, flash, redirect, url_for
from threading import Lock

from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef, Literal

from gen import ID_gen_val
from gen import ID_gen_var
from werkzeug.utils import secure_filename


app = flask.Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.secret_key = b'\x13f0\x97\x86QUOHc\xfa\xe7(\xa1\x8d1'

m = Lock()
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# server_url = "http://lasagna.eecs.umich.edu:5000"
server_url = "http://127.0.0.1:5000"
g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg", server_url + "/")

dg = Graph('Sleepycat', identifier="dependency")
dg.open('db', create=True)
dg.bind("kg", server_url + "/")

ns = Namespace(server_url + "/")

# predicates
hasHistory = ns.hasHistory
hasKGPLValue = ns.hasKGPLValue
valueHistory = ns.valueHistory
hasValue = ns.hasValue
kgplType = ns.kgplType
pyType = ns.pyType
hasComment = ns.hasComment
belongTo = ns.belongTo
derive = ns.derive

# kgplType
kgplValue = ns.kgplValue
kgplVariable = ns.kgplVariable


@app.route("/", methods=['GET'])
def main():
    return "KGPL", 200

"""
@app.route("/nextval", methods=['GET'])
def return_val_id():
    vid = ID_gen_val.next()
    context = {
        "id": ns["val/" + str(vid)]
    }
    return flask.jsonify(**context), 200


@app.route("/nextvar", methods=['GET'])
def return_var_id():
    vid = ID_gen_var.next()
    context = {
        # "id": "var/" + str(vid)
        "id": ns["var/" + str(vid)]
    }

    return flask.jsonify(**context), 200
"""

@app.route("/val", methods=['POST'])
def post_val():
    d = request.form
    if "val" not in d or "pyType" not in d or "comment" not in d or "user" not in d or "dependency" not in d:
        flask.abort(400)
    dependency = json.loads(d["dependency"])
    if d["pyType"] == "Image":
        if "file" not in request.files:
            flask.abort(400)
        image = json.loads(d["val"])
        if "filename" not in image:
            flask.abort(400)
        if not allowed_file(image["filename"]):
            flask.abort(400)
    m.acquire()
    vid = ID_gen_val.current
    for de in dependency:
        did = int(de[de.rfind('/') + 1:])
        if did >= vid:
            flask.abort(400)
    vid = ID_gen_val.next()
    m.release()
    url = URIRef(ns["val/" + str(vid)])
    if d["pyType"] == "Image":
        request.files["file"].save(os.path.join(app.config['UPLOAD_FOLDER'], str(vid)))
    # print(url)
    # if using different namespace for val and var, we should change ?x into kgplValue
    val = Literal(d["val"])
    pyt = Literal(d["pyType"])
    com = Literal(d["comment"])
    ownername = Literal(d["user"])
    g.add((url, belongTo, ownername))
    for de in dependency:
        durl = URIRef(de)
        dg.add((durl, derive, url))
    g.add((url, hasValue, val))
    g.add((url, kgplType, kgplValue))
    g.add((url, pyType, pyt))
    g.add((url, hasComment, com))
    context = { "url": str(url) }
    return flask.jsonify(**context), 201


@app.route("/var", methods=['POST'])
def post_var():
    d = request.get_json()
    if "val_id" not in d or "comment" not in d or "user" not in d:
        flask.abort(400)
    val_url = URIRef(d["val_id"])

    # check if val_id is valid
    qres = g.query(
        """ASK {
            {?url kg:kgplType kg:kgplValue}
            }
        """,
        initBindings={'url': val_url}
    )
    for x in qres:
        if not x:
            print("val id not exist")
            flask.abort(400)
    m.acquire()
    vid = ID_gen_var.next()
    m.release()
    url = URIRef(ns["var/" + str(vid)])
    ts = time.time()
    ts_url = URIRef(url + "/ts/" + str(ts))
    com = Literal(d["comment"])
    ownername = Literal(d["user"])
    g.add((url, belongTo, ownername))
    g.add((url, valueHistory, ts_url))
    g.add((ts_url, hasKGPLValue, val_url))
    g.add((url, kgplType, kgplVariable))
    g.add((ts_url, hasComment, com))
    context = {"url": url, "timestamp": ts}
    return flask.jsonify(**context), 201


@app.route("/load/val", methods=['GET'])
def get_val():
    vid = request.args.get('vid')
    url = URIRef(vid)
    qres = g.query(
        """SELECT ?val ?pyt ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasComment ?com ;
               kg:hasValue ?val ;
               kg:belongTo ?user .
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for val, pyt, com, user in qres:
            context = {
                "val": str(val),
                "pyt": str(pyt),
                "comment": str(com),
                "user": str(user)
            }
            dqres = dg.query(
                """SELECT ?durl
                WHERE {
                    ?durl kg:derive ?url .
                }""",
                initBindings={'url': url}
            )
            if len(dqres) == 0:
                context["dependency"] = []
            else:
                dependency = []
                for durl, in dqres:
                    dependency.append(str(durl))
                context["dependency"] = dependency
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/load/var", methods=['GET'])
def get_var():
    vid = request.args.get('vid')
    url = URIRef(vid)
    # print(url)
    qres = g.query(
        """SELECT ?ts ?val_url ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                kg:belongTo ?user ;
                kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_url ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for ts, val_url, com, user in qres:
            val_url = str(val_url)
            ts = str(ts)
            com = str(com)
            actual_ts = float(ts[ts.rfind('/') + 1:])
            context = {
                "val_id": val_url,
                "timestamp": actual_ts,
                "comment": com,
                "user": user
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/var", methods=['PUT'])
def set_var():
    d = request.get_json()
    if "vid" not in d or "val_id" not in d or "timestamp" not in d or "new_comment" not in d:
        flask.abort(400)
    url = URIRef(d["vid"])
    val_url = URIRef(d["val_id"])
    ts = d["timestamp"]
    # print("URI: ", url)
    qres = g.query(
        """SELECT ?ts_url
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                 kg:valueHistory ?ts_url .
        }""",
        initBindings={'url': url}
    )
    ots_url = URIRef(url+"/ts/"+str(ts))
    # print(ots_url)
    # ots_url = URIRef(os.path.join(url, str(ts)))
    if len(qres) == 1:
        for ts_url, in qres:
            if ts_url != ots_url:
                print(ts_url)
                print(type(ts_url))
                print(type(ots_url))
                print(ots_url)
                print("version conflict")
                flask.abort(403)
            qres = g.query(
                """ASK {
                ?url kg:kgplType kg:kgplValue
                }""",
                initBindings={'url': val_url}
            )
            for x in qres:
                if not x:
                    print("val id not exist")
                    flask.abort(400)
            ts = time.time()
            nts_url = url+"/ts/"+str(ts)
            # nts_url = URIRef(os.path.join(url, str(ts)))
            g.remove((url, valueHistory, None))
            g.add((url, valueHistory, nts_url))
            g.add((nts_url, hasKGPLValue, val_url))
            g.add((nts_url, hasHistory, ts_url))
            g.add((nts_url, hasComment, Literal(d["new_comment"])))
            context = {"timestamp": ts}
            return flask.jsonify(**context), 201
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        print("Multiple result found!")
        return flask.abort(500)


@app.route("/gethistory", methods=['GET'])
def gethistory():
    d = request.get_json()
    if "vid" not in d:
        flask.abort(400)
    url = URIRef(d["vid"])
    qres = g.query(
        """SELECT ?ts ?val_uri
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                 kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_uri ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    rst = []
    if len(qres) != 1:
        print(len(qres))
        print("place one")
        flask.abort(500)
    for x, val_uri in qres:
        current_ts = x
        # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
        rst.append(val_uri)
        while True:
            qres = g.query(
                """SELECT ?ts ?val_uri
                WHERE {
                    ?current_ts kg:hasHistory ?ts .
                    ?ts kg:hasKGPLValue ?val_uri .
                }""",
                initBindings={'current_ts': current_ts}
            )
            if len(qres) == 0:
                break
            elif len(qres) != 1:
                print("place two")

                flask.abort(500)
            for ts, val_uri in qres:
                current_ts = ts
                # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
                rst.append(val_uri)
        context = {"list": rst}
        return flask.jsonify(**context), 200


@app.route("/getLatest", methods=['GET'])
def getLatest():
    d = request.get_json()
    if "val_id" not in d:
        flask.abort(400)

    url = ns[str(d["val_id"])]
    qres = g.query(
        """SELECT ?ts ?val_uri
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
               kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_uri
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for ts, val_url in qres:
            val_url = str(val_url)
            ts = str(ts)
        actual_val_id = int(val_url[val_url.rfind('/') + 1:])
        actual_ts = float(ts[ts.rfind('/') + 1:])
        context = {
            "val_id": actual_val_id,
            "timestamp": actual_ts
        }
        return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/val/<vid>", methods=['GET'])
def frontend_val(vid):
    url = ns["val/" + str(vid)]

    print(url)
    qres = g.query(
        """SELECT ?val ?pyt ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasValue ?val ;
               kg:hasComment ?com ;
               kg:belongTo ?user.
        }""",
        initBindings={'url': url}
    )
    pandas.set_option('display.float_format', lambda x: '%.1f' % x)
    if len(qres) == 1:
        for val, pyt, com, user in qres:
            file_name = None
            current_value = pandas.read_json(val).to_html() if str(
                pyt) == "DataFrame" else str(val)

            if str(pyt) == "Relation":
                # a = json.loads(str(val))["trace"]

                # b = json.loads(a)
                # print(type(b))
                context = {
                    "KGPLValue": str(url),
                    "entity_id": json.loads(str(val))["entity_id"],
                    "Python_Type": str(pyt),
                    "Comments": str(com),
                    "Owner": str(user),
                    "df": pandas.read_json(json.loads(str(val))["df"]).to_html(),
                    "query_str": json.loads(str(val))["query_str"],
                }

                return flask.render_template("relation_val_meta_page.html", **context)
            elif str(pyt) == "Image":
                file_name = vid[vid.rfind('/') + 1:]

            context = {
                "KGPLValue": str(url),
                "Current_Value": current_value,
                "Python_Type": str(pyt),
                "Comments": str(com),
                "Owner": str(user),
                "file_name":file_name
            }
            return flask.render_template("val_meta_page.html", **context)
            # return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        print("Multiple Results Found, should not happen!")
        return flask.abort(500)


@app.route("/var/<vid>", methods=['GET'])
def frontend_meta_var(vid):
    url = ns["var/" + str(vid)]
    his = []
    owner = ""
    qres = g.query(
        """SELECT ?ts ?val_url ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                kg:valueHistory ?ts ;
                kg:belongTo ?user.
            ?ts kg:hasKGPLValue ?val_url ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for ts, val_url, com, user in qres:
            his.append(ts)
            val_url = str(val_url)
            ts_for_query = ts
            ts = str(ts)
            com = str(com)
            # print(val_url)
            # actual_val_id = int(val_url[val_url.rfind('/') + 1:])
            actual_ts = float(ts[ts.rfind('/') + 1:])
            owner = str(user)

            while True:
                qres = g.query(
                    """SELECT ?history ?val_uri 
                    WHERE {
                        ?url kg:hasComment ?com ;
                             kg:hasHistory ?history ;
                             kg:hasKGPLValue ?val_uri .
                    }""",
                    initBindings={'url': ts_for_query}
                )
                print(ts)
                if len(qres) == 0:
                    print("end")
                    break
                elif len(qres) != 1:
                    print("place two")

                    flask.abort(500)
                for history, val_uri in qres:
                    ts_for_query = history
                    # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
                    his.append(history)

            context = {
                "KGPLVariable": str(url),
                "Currently_containing_KGPLValue": val_url,
                "Current_comment": com,
                "Last_modified_timestamp": actual_ts,
                "Last_modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(actual_ts)),
                "History": his,
                "Owner": str(owner)
            }

            return flask.render_template("var_meta_page.html", **context)
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


"""frontend"""


@app.route("/graph1.svg", methods=['GET'])
def get_svg():
    return flask.send_file("graph1.svg")


@app.route("/compact/<vid>", methods=['GET'])
def get_compacthtml(vid):
    url = ns["val/" + str(vid)]
    qres = g.query(
        """SELECT ?kgval ?ty
        WHERE {
            ?url kg:hasValue ?kgval ;
                kg:pyType ?ty .
        }""",
        initBindings={'url': url}
    )
    if len(qres) != 1:
        print(url)
        return "ERROR: data not found or data found not single"
    for val, ty in qres:
        see_more_info = "<p> See more info <a href='val/" + \
            str(vid) + "'><u> here </u></a> </p>"
        val = json.loads(val)
        if str(ty) == "Image":
            if "filename" not in val:
                print("cannot find filename")
                flask.abort(500)
            filename = val["filename"]
            filetype = filename.rsplit('.', 1)[1].lower()
            if filetype in ['png', 'jpg', 'jpeg', 'gif']:
                header = "<h3> Data type: image</h3> <h3> URL: " + \
                    str(url) + "</h3>"
                content = "<img src='" + \
                    os.path.join(
                        app.config['UPLOAD_FOLDER'], str(vid)) + "' alt=image width='35%' height='35%'>"
                return json.dumps({"html": header + content + see_more_info})
            else:
                header = "<h3> Data type: " + \
                    val["__file__"] + " file</h3> <h3>URL: " + \
                    str(url) + "</h3>"
                return json.dumps({"html": header + see_more_info})
        elif str(ty) == "Relation":
            return ""
        elif str(ty) == "DataFrame":
            return ""
        elif str(ty) == "dict":
            header = "<h3> Data type: " + \
                str(ty) + "</h3><h3> URL: " + str(url) + "</h3>"
            return json.dumps({"val": val, "header": header, "more_info": see_more_info})
        else:
            header = "<h3> Data type: " + \
                str(ty) + "</h3><h3> URL: " + str(url) + "</h3>"
            if str(ty) == "tuple":
                val = tuple(val)
            content = str(val)
            if len(content) > 300:
                content = content[:300]
                content = "<div id='pre_text'><pre>" + content + "...</pre></div>"
            else:
                content = "<div id='pre_text'><pre>" + content + "</pre></div>"
            return json.dumps({"html": header + content + see_more_info})
        
#
# @app.route("/getCollapsedGraph", methods=['GET'])
# def get_collapsed_graph():
#    left = requests.get_json()
#    nodes = left["nodes"]
#    nodes.sort()
#    edges = left["edges"]
#    depend_dict = {}
#    user_dict = {}
#    var_dict = {}
#    for e in edges:
#        if e[0] in depend_dict:
#            depend_dict[e[0]].append(e[1])
#        else:
#            depend_dict[e[0]] = [e[1]]
#    for vn in nodes:
#        url = ns["val/" + str(vn)]
#        qres = g.query(
#            """SELECT ?user
#            WHERE {
#                ?url kg:belongTo ?user .
#            }""",
#            initBindings={'url': url}
#        )
#        if len(qres) != 1:
#            print("user")
#            flask.abort(500)
#        else:
#            for user, in qres:
#                user_dict[vn] = str(user)
#    cluster = []
#    cluster_dict = {}
#    for x in nodes:
#        added = False
#        if user_dict[x] == "anonymous":
#            cluster.append(["anonymous", [x]])
#            # cluster_depend.append("don't care")
#            cluster_dict[x] = len(cluster) - 1
#            continue
#        lowest_level = 0
#        for j in depend_dict[x]:
#            if cluster_dict[j] > lowest_level:
#                lowest_level = cluster_dict[j]
#        for i in range(lowest_level, len(cluster)):
#            l = cluster[i]
#            if l[0] == user_dict[x]:
#                added = True
#                cluster[i][1].append(x)
#                cluster_dict[x] = i
#                break
#            """
#            qres = g.query(
#                """SELECT ?var_url
#                WHERE {
#                    ?var_url kg:kgplType kg:kgplVariable ;
#                        kg:valueHistory ?ts .
#                    ?ts kg:hasKGPLValue ?val_url .
#                }""",
#                initBindings={'val_url': url}
#            )
#            if len(qres) != 0:
#                for var_url, in qres:
#                    str(var_url)[str(var_url).rfind("/") + 1:]
#            """
#    with open("vis.gv", "w") as file:
#        file.write("digraph G {\n")
#        for i,l in enumerate(cluster):
#            file.write("subgraph cluster_" + str(i) + " {\nnode [style=filled];\ncolor=blue;\nlabel=" + l[0] + ";\n")
#            for node in l[1]:
#                val_url = ns["val/" + str(node)]
#                qres = g.query(
#                    """SELECT ?var_url
#                    WHERE {
#                        ?var_url kg:kgplType kg:kgplVariable ;
#                            kg:valueHistory ?ts .
#                        ?ts kg:hasKGPLValue ?val_url .
#                    }""",
#                    initBindings={'val_url': val_url}
#                )
#                if len(qres) == 0:
#                    file.write("val" + str(node) + ";\n")
#                else:
#                    label = ""
#                    c = 1
#                    for var_url, in qres:
#                        label += "var" + str(var_url)[str(var_url).rfind("/") + 1:]
#                        if c == len(qres):
#                            break;
#                        label += ", "
#                        c += 1
#                    file.write("subgraph clusterofval" + str(node) + " {\nnode [style=filled];\ncolor=black;\nlabel=" + label + ";\n")
#                    file.write("val" + str(node) + ";\n")
#                    file.write("}\n")
#            file.write("}\n")
#        for x in depend_dict:
#            vn = "val" + str(x)
#            for t in depend_dict[x]:
#                file.write("val" + str(t) + " -> " + vn + ";\n")
#        file.write("}\n")
#    os.system("dot -Tpng vis.gv -o templates/graph.png")


@app.route("/visualization", methods=['GET'])
def visual():
    user_dict = {}
    depend_dict = {}
    current = ID_gen_val.current
    for vn in range(0, current):
        url = ns["val/" + str(vn)]
        qres = g.query(
            """SELECT ?user
            WHERE {
                ?url kg:belongTo ?user .
            }""",
            initBindings={'url': url}
        )
        if len(qres) != 1:
            print("user")
            flask.abort(500)
        else:
            for user, in qres:
                user_dict[vn] = str(user)
                # json["values"][str(url)] = str(user)
        depend_dict[vn] = []
        dqres = dg.query(
            """SELECT ?durl
            WHERE {
                ?durl kg:derive ?url .
            }""",
            initBindings={'url': url}
        )
        for durl, in dqres:
            src = int(str(durl)[str(durl).rfind("/") + 1:])
            depend_dict[vn].append(src)
    cluster = []
    cluster_dict = {}
    # cluster_depend = []
    for x in range(0, current):
        added = False
        if user_dict[x] == "anonymous":
            cluster.append(["anonymous", [x]])
            # cluster_depend.append("don't care")
            cluster_dict[x] = len(cluster) - 1
            continue
        lowest_level = 0
        for j in depend_dict[x]:
            if cluster_dict[j] > lowest_level:
                lowest_level = cluster_dict[j]
        for i in range(lowest_level, len(cluster)):
            l = cluster[i]
            if l[0] == user_dict[x]:
                added = True
                cluster[i][1].append(x)
                cluster_dict[x] = i
                break
            """
            if depend_dict[x] == []:
                cluster[i][1].append(x)
                added = True
                break
            depend_set = {cluster_dict[j] for j in depend_dict[x]}
            if cluster_depend < lowest_level:
                continue
            if depend_set > cluster_depend[i]:
                cluster_depend[i] = depend_set
            cluster[i][1].append(x)
            cluster_dict[x] = i
            added = True
            break
            """
        if not added:
            cluster.append([user_dict[x], [x]])
            cluster_dict[x] = len(cluster) - 1
            # cluster_depend.append({cluster_dict[j] for j in depend_dict[x]})
        """
        print(cluster)
        print(cluster_depend)
        print(cluster_dict)
        """
    with open("vis.gv", "w") as file:
        file.write("digraph G {\n")
        for i, l in enumerate(cluster):
            title = ""
            for idx, node in enumerate(l[1]):
                title += str(node)
                title += "_"
            file.write("subgraph clusterusr_" + title +
                       " {\nnode [style=filled];\ncolor=blue;\nlabel=" + l[0] + ";\n")
            for node in l[1]:
                val_url = ns["val/" + str(node)]
                qres = g.query(
                    """SELECT ?var_url
                    WHERE {
                        ?var_url kg:kgplType kg:kgplVariable ;
                            kg:valueHistory ?ts .
                        ?ts kg:hasKGPLValue ?val_url .
                    }""",
                    initBindings={'val_url': val_url}
                )
                if len(qres) == 0:
                    file.write("val" + str(node) + ";\n")
                else:
                    label = ""
                    c = 1
                    for var_url, in qres:
                        label += "var" + \
                            str(var_url)[str(var_url).rfind("/") + 1:]
                        if c == len(qres):
                            break
                        label += ", "
                        c += 1
                    file.write("subgraph clustervar_" + str(node) +
                               "_ {\nnode [style=filled];\ncolor=black;\nlabel=" + label + ";\n")
                    file.write("val" + str(node) + ";\n")
                    file.write("}\n")
            file.write("}\n")
        for x in depend_dict:
            vn = "val" + str(x)
            for t in depend_dict[x]:
                file.write("val" + str(t) + " -> " + vn + ";\n")
        file.write("}\n")
    if os.path.exists("graph1.svg"):
        os.remove("graph1.svg")
    os.system("dot -Tsvg vis.gv -o graph1.svg")
    return flask.render_template("visualization.html")


@app.route("/css/graphviz.svg.css", methods=['GET'])
def get_css():
    return flask.send_file("css/graphviz.svg.css")


@app.route("/js/jquery.graphviz.svg.js", methods=['GET'])
def get_js():
    return flask.send_file("js/jquery.graphviz.svg.js")


@app.route("/var/<vid>", methods=['GET'])
def frontend_var(vid):
    url = ns["var/" + str(vid)]
    his = []
    qres = g.query(
        """SELECT ?ts ?val_url ?com
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
               kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_url ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for ts, val_url, com in qres:
            his.append(ts)
            val_url = str(val_url)
            ts_for_query = ts
            ts = str(ts)
            com = str(com)
            # print(val_url)
            # actual_val_id = int(val_url[val_url.rfind('/') + 1:])
            actual_ts = float(ts[ts.rfind('/') + 1:])

            while True:
                qres = g.query(
                    """SELECT ?history ?val_uri
                    WHERE {
                        ?url kg:hasComment ?com ;
                             kg:hasHistory ?history ;
                             kg:hasKGPLValue ?val_uri .
                    }""",
                    initBindings={'url': ts_for_query}
                )
                print(ts)
                if len(qres) == 0:
                    print("end")
                    break
                elif len(qres) != 1:
                    print("place two")

                    flask.abort(500)
                for history, val_uri in qres:
                    ts_for_query = history
                    # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
                    his.append(history)
            context = {
                "KGPLVariable": str(url),
                "Currently containing KGPLValue": val_url,
                "Current comment": com,
                "Last modified timestamp": actual_ts,
                "Last modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(actual_ts)),
                "History": his
            }

            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/var/<vid>/ts/<ts>", methods=['GET'])
def frontend_timestamp(vid, ts):
    url = ns["var/" + str(vid) + "/ts/" + str(ts)]
    # qres = g.query(
    #     """SELECT ?ts ?val_url
    #     WHERE {
    #         ?url kg:kgplType kg:kgplVariable ;
    #            kg:valueHistory ?ts .
    #         ?ts kg:hasKGPLValue ?val_url .
    #     }""",
    #     initBindings={'url': url}
    # )

    qres = g.query(
        """SELECT ?kgval
        WHERE {
            ?url kg:hasKGPLValue ?kgval.
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for kgval, in qres:
            context = {
                "KGPLVariable \""+str(url)+"\" at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(ts))),
                "timestamp": ts,
                "KGPLValue": kgval
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


def close_graph():
    g.close()
    dg.close()
    print("server is closing")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print("No file part")
            return redirect("/upload")
        file = request.files['file']
        file_id = request.files['value_id']
        # print(file_id)
        # print(type(file_id))

        # print(file_id.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            print("No selected file")
            return redirect("/upload")
        if file and allowed_file(file.filename):
            # print(type(file.filename))
            # print(file.filename)

            # print(type(add_id))
            # new_name_before = "val_"+add_id+"_" + str(file.filename)
            # print(new_name_before)
            new_name = secure_filename(
                "val_"+file_id.filename+"_"+str(file.filename))
            print("allow")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            # add a kgplvalue
            context = {
                "filename_stored": new_name
            }
            return flask.jsonify(**context), 200

    # return flask.render_template("upload.html")


@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    print(app.config['UPLOAD_FOLDER']+filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename), 200


atexit.register(close_graph)
