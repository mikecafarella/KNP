import atexit
import os
import time

import flask
from flask import request
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef, Literal

from gen import ID_gen_val
from gen import ID_gen_var

app = flask.Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# server_url = "http://lasagna.eecs.umich.edu:5000"
server_url = "http://127.0.0.1:5000"
# server_url = "http://global.url"  # The namespace, should be adjusted on every server
g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg", server_url + "/")
ns = Namespace(server_url + "/")

# predicates
hasHistory = ns.hasHistory
hasKGPLValue = ns.hasKGPLValue
valueHistory = ns.valueHistory
hasValue = ns.hasValue
kgplType = ns.kgplType
pyType = ns.pyType
hasComment = ns.hasComment

# kgplType
kgplValue = ns.kgplValue
kgplVariable = ns.kgplVariable


@app.route("/", methods=['GET'])
def main():
    cur_val = []
    qres = g.query(
        """SELECT ?url ?com
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasComment ?com;
               kg:hasValue ?val .
        }""",
    )

    for url,com in qres:
        cur_val.append((url,com))
    cur_var = []
    qres = g.query(
        """SELECT ?url ?com
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                 kg:valueHistory ?ts .
            ?ts  kg:hasComment ?com;
                 kg:hasKGPLValue ?val .
        }""",
    )

    for url, com in qres:
        cur_var.append((url,com))
    context = {
        "KGPLValue": cur_val,
        "KGPLVariable":cur_var
    }

    return flask.jsonify(**context), 200


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


@app.route("/val", methods=['POST'])
def post_val():
    d = request.get_json()
    if "id" not in d or "val" not in d or "pyType" not in d or "comment" not in d:
        flask.abort(400)
    url = URIRef(d["id"])
    # print(url)
    # if using different namespace for val and var, we should change ?x into kgplValue
    qres = g.query(
        """ASK {
            ?url kg:kgplType kg:kgplValue
            }""",
        initBindings={'url': url}
    )
    for x in qres:
        if x:
            flask.abort(400)
    val = Literal(d["val"])
    pyt = Literal(d["pyType"])
    com = Literal(d["comment"])
    g.add((url, hasValue, val))
    g.add((url, kgplType, kgplValue))
    g.add((url, pyType, pyt))
    g.add((url, hasComment, com))
    return "", 201


@app.route("/var", methods=['POST'])
def post_var():
    d = request.get_json()
    if "id" not in d or "val_id" not in d or "comment" not in d:
        flask.abort(400)
    val_url = URIRef(d["val_id"])
    url = URIRef(d["id"])

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

    # check if current id exist
    qres = g.query(
        """ASK {
            ?url kg:kgplType kg:kgplVariable
            }""",
        initBindings={'url': url}
    )
    for x in qres:
        if x:
            print("current id exists")
            flask.abort(400)
    ts = time.time()
    ts_url = URIRef(url + "/ts/" + str(ts))
    com = Literal(d["comment"])
    g.add((url, valueHistory, ts_url))
    g.add((ts_url, hasKGPLValue, val_url))
    g.add((url, kgplType, kgplVariable))
    g.add((ts_url, hasComment, com))
    context = {"timestamp": ts}
    return flask.jsonify(**context), 201


@app.route("/load/val", methods=['GET'])
def get_val():
    vid = request.args.get('vid')
    url = URIRef(vid)
    qres = g.query(
        """SELECT ?val ?pyt ?com
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasComment ?com;
               kg:hasValue ?val .
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for val, pyt, com in qres:
            context = {
                "val": str(val),
                "pyt": str(pyt),
                "comment": str(com)
            }
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
            val_url = str(val_url)
            ts = str(ts)
            com = str(com)
            actual_ts = float(ts[ts.rfind('/') + 1:])
            context = {
                "val_id": val_url,
                "timestamp": actual_ts,
                "comment": com
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
        """SELECT ?val ?pyt ?com
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasValue ?val ;
               kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for val, pyt, com in qres:
            context = {
                "KGPLValue": str(url),
                "Current Value: ": str(val),
                "Python Type": str(pyt),
                "Comments": str(com)
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        print("Multiple Results Found, should not happen!")
        return flask.abort(500)


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
                "KGPLVariable \""+str(url)+"\" at":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(ts))),
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
    print("server is closing")


atexit.register(close_graph)
