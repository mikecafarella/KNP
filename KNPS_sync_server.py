import flask
import os
import pickle
import json
import jsonpickle
from kgpl import KGPLValue, KGPLVariable
import KNPSStore

app = flask.Flask(__name__)
s = KNPSStore.KNPSStore(None)


@app.route("/val/<fileid>", methods=['GET', 'POST'])
def ReturnValue(fileid):
    # file_path = os.path.join("val", fileid)
    if flask.request.method == 'GET':
        val = s.GetValue(fileid)
        if not val:
            return flask.abort(404)
        context = {"value": jsonpickle.encode(val)}
        return flask.jsonify(**context), 200
    else:
        val = jsonpickle.decode(flask.request.json["value"])
        s.StoreValues([val])
        s.PushValues()
        context = {
            "id": fileid,
            "value": jsonpickle.encode(val)
        }
        return flask.jsonify(**context), 201


@app.route("/var/<fileid>", methods=['GET', 'PUT'])
def ReturnVariable(fileid):
    # file_path = os.path.join("var", fileid)
    if flask.request.method == 'GET':
        var = s.GetVariable(fileid)
        if not var:
            return flask.abort(404)
        else:
            context = {"var": jsonpickle.encode(var)}
            return flask.jsonify(**context), 200
    else:
        timestamp = flask.request.json["timestamp"]
        val = jsonpickle.decode(flask.request.json["value"])
        var = s.SetVariable(fileid, val, timestamp)
        if not var:
            return flask.abort(404)
        context = {
            "var": jsonpickle.encode(var)
        }
        return flask.jsonify(**context), 201


@app.route("/var", methods=['POST'])
def RegisterVariable():
    data = flask.request.json
    print(data)
    value = jsonpickle.decode(data["value"])
    timestamp = data["timestamp"]
    filename = s.RegisterVariable(value, timestamp)
    path = os.path.join("var", filename)
    infile = open(path, "r")
    context = {
        "varName": filename,
        "var": infile.read()
    }
    infile.close()
    return flask.jsonify(**context), 201

