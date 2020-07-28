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

server_url = "http://lasagna.eecs.umich.edu:80"
g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg", server_url + "/")
ns = Namespace(server_url + "/")

# predicates
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
    # if using different namespace for val and var, we should change ?x into kgplValue
    qres = g.query(
        """ASK {
            %s kg:kgplType ?x
            }""" % url
    )
    if qres:
        flask.abort(400)
    val = Literal(json.dumps(d["val"]))
    pyt = Literal(d["pyType"])
    ts = time.time()
    timestamp = URIRef(os.path.join(url, ts))
    g.add((url, valueHistory, timestamp))
    g.add((timestamp, hasValue, val))
    g.add((url, kgplType, kgplValue))
    g.add((url, pyType, pyt))
    context = {"timestamp": ts}
    return flask.jsonify(**context), 201

@app.route("/load/val/<vid>", methods=['GET'])
def get_val(vid):
    url = os.path.join(server_url, str(vid))
    qres = g.query(
        """SELECT ?ts ?val ?pyt
        WHERE {
            %s kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt
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
    elif: 
        return flask.abort(400)
        
    
#@app.route(os.path.join(load_url, "<id>"), methods=['GET'])
#def return_val_or_var(id):
