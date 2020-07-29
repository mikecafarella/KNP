from gen import ID_gen
import flask
from flask import request
import json
import time
import os
import atexit
import rdflib
from rdflib import Graph
from rdflib import store
from rdflib import Namespace
from rdflib import URIRef, Literal

app = flask.Flask(__name__)

server_url = "http://127.0.0.1:5000"
g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg", server_url + "/")
ns = Namespace(server_url + "/")

# predicates
historyOf = ns.historyOf
pointsTo = ns.pointsTo
valueHistory = ns.valueHistory
hasValue = ns.hasValue
kgplType = ns.kgplType
pyType = ns.pyType

# kgplType
kgplValue = ns.kgplValue
kgplVariable = ns.kgplVariable

@app.route("/next", methods=['GET'])
def return_id():
    vid = ID_gen.next()
    context = {   
        "id": vid
    }
    return flask.jsonify(**context), 200

@app.route("/val", methods=['POST'])
def post_val():
    d = request.get_json()
    if "id" not in d or "val" not in d or "pyType" not in d or "timestamp" not in d:
        flask.abort(400)
    url = ns[str(d["id"])]
    print(url)
    # if using different namespace for val and var, we should change ?x into kgplValue
    qres = g.query(
        """ASK {
            ?url kg:kgplType ?x
            }""" , 
            initBindings={'url': URIRef(url)}
    )
    for x in qres:
        if x:
            flask.abort(400)
    val = Literal(json.dumps(d["val"]))
    pyt = Literal(d["pyType"])
    ts = time.time()
    timestamp = URIRef(os.path.join(url, str(ts)))
    g.add((url, valueHistory, timestamp))
    g.add((timestamp, hasValue, val))
    g.add((url, kgplType, kgplValue))
    g.add((url, pyType, pyt))
    context = {"timestamp": ts}
    return flask.jsonify(**context), 201

@app.route("/var", methods=['POST'])
def post_var():
    d = request.get_json()
    if "id" not in d or "val_id" not in d:
        flask.abort(400)
    val_url = ns[str(d["val_id"])]
    url = ns[str(d["id"])]

    # check if val_id is valid
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

    # check if current id exist
    qres = g.query(
        """ASK {
            ?url kg:kgplType ?x
            }""",
            initBindings={'url': url}
    )
    for x in qres:
        if x:
            flask.abort(400)
    g.add((url, pointsTo, val_url))
    g.add((url, kgplType, kgplVariable))
    return "", 201

@app.route("/load/val/<vid>", methods=['GET'])
def get_val(vid):
    url = ns[str(vid)]
    print(url)
    qres = g.query(
        """SELECT ?ts ?val ?pyt
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:valueHistory ?ts .
            ?ts kg:hasValue ?val .
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for ts, val, pyt in qres:
            actual_ts = float(ts[str(ts).rfind('/') + 1:])
            context = {
                "timestamp": actual_ts,
                "val": json.loads(str(val)),
                "pyt": str(pyt)
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else: 
        return flask.abort(400)
        
    
@app.route("/load/var/<vid>", methods=['GET'])
def get_var(vid):
    url = ns[str(vid)]
    qres = g.query(
        """SELECT ?val
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
               kg:pointsTo ?val .
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for x, in qres:
            val_url = str(x)
        print(val_url)
        actual_val_id = int(val_url[val_url.rfind('/') + 1 :])
        context = {
            "val_id": actual_val_id
        }
        return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else: 
        return flask.abort(400)


@app.route("/var", methods=['PUT'])
def set_var():
    d = request.get_json()
    if "vid" not in d or "val_id" not in d:
        flask.abort(400)
    url = ns[str(d["vid"])]
    val_url = ns[str(d["val_id"])]
    qres = g.query(
        """SELECT ?val
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
               kg:pointsTo ?val .
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
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
        g.remove((url, pointsTo, None))
        g.add((url, pointsTo, val_url))
        return "", 201
    elif len(qres) == 0:
        return flask.abort(404)
    else: 
        return flask.abort(500)


@app.route("/val", methods=['PUT'])
def set_val():
    d = request.get_json()
    if "vid" not in d or "new_val" not in d or "timestamp" not in d:
        flask.abort(400)
    url = ns[str(d["vid"])]
    qres = g.query(
        """SELECT ?ts
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:valueHistory ?ts .
        }""",
        initBindings={'url': url}
    )
    if len(qres) != 1:
        if len(qres) == 0:
            flask.abort(404)
        else:
            print("different kgvals have a same id")
            flask.abort(500)
    ts_url = URIRef(os.path.join(url, str(d["timestamp"])))
    for ts, in qres:
        if str(ts) == str(ts_url):
            nts = time.time()
            nts_url = URIRef(os.path.join(url, str(nts)))
            new_val = Literal(json.dumps(d["new_val"]))
            g.add((url, valueHistory, nts_url))
            g.add((nts_url, hasValue, new_val))
            g.add((ts_url, historyOf, nts_url))
            g.remove((url, valueHistory, ts_url))
            g.remove((url, pyType, None))
            g.add((url, pyType, Literal(d["pyType"])))
            context = {"timestamp": nts}
            return flask.jsonify(**context), 201
        else:
            print("changes not based on the newest version")
            flask.abort(403)


def close_graph():
    g.close()
    print("server is closing")

atexit.register(close_graph)    