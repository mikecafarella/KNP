from gen import ID_gen
import flask
import json
from flask import request
import time
import os
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
    if qres:
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
    qres = g.query(
        """ASK {
            %s kg:kgplType kg:kgplValue
            }""" % url
    )
    if not qres:
        flask.abort(404)
    qres = g.query(
        """ASK {
            %s kg:kgplType ?x
            }""" % url
    )
    if qres:
        flask.abort(400)
    g.add((url, pointsTo, val_url))
    g.add((url, kgplType, kgplVariable))
    return "", 201

@app.route("/load/val/<vid>", methods=['GET'])
def get_val(vid):
    url = ns[str(vid)]
    qres = g.query(
        """SELECT ?ts ?val ?pyt
        WHERE {
            %s kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:valueHistory ?ts .
            ?ts kg:hasValue ?val
        }""" % url
    )
    if len(qres) == 1:
        ts = qres[0][0]
        val = json.loads(qres[0][1])
        pyt = qres[0][2]
        context = {
            "timestamp": ts,
            "val": val,
            "pyt": pyt
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
            %s kg:kgplType kg:kgplVariable ;
               kg:pointsTo ?val .
        }""" % url
    )
    if len(qres) == 1:
        val_id = qres[0]
        context = {
            "val_id": val_id
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
            %s kg:kgplType kg:kgplVariable ;
               kg:pointsTo ?val .
        }""" % url
    )
    if len(qres) == 1:
        g.remove((url, pointsTo, None))
        g.add((url, pointsTo, val_url))
        return "", 201
    elif len(qres) == 0:
        return flask.abort(404)
    else: 
        return flask.abort(400)

    