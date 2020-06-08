from datetime import datetime

import flask
import pickle
import json
from kgpl import KNPSStore
from sqlalchemy.orm import session
from kgpl.KNPSStore import Session
import server

app = flask.Flask(__name__)
s = KNPSStore(None)

APPLICATION_ROOT = '/'


@app.route("/", methods=['GET', 'POST'])
def main():
    if flask.request.method == 'POST':
        vname = flask.request.form['Variable_Name']
        print(vname)
        var = s.GetVariable(vname)
        his = var.historical_vals
        print(his)
        print("@@@@@@@@@@@@@@@@@@@@@@", type(his))
        # pretty = json.dumps(his, sort_keys=True, indent=4,
        #                     separators=(',', ': '))

        pretty_time = []
        for onehis in his:
            value_value = s.GetValue(onehis[1])

            pretty_time.append((datetime.fromtimestamp(onehis[0]).strftime(
                '%Y-%m-%d %H:%M:%S'), onehis[1], type(value_value).__name__,
                                value_value.val),
            )

        context = {
            "vname": vname,
            "var": pretty_time
        }
        return flask.render_template("result.html", **context)

    else:
        context = {"users": "hardcode"}
        # return flask.jsonify(**context), 200
        # return flask.render_template("index.html", **context)

        return flask.render_template("index.html", **context)


@app.route("/val/<fileid>", methods=['GET', 'POST'])
def ReturnValue(fileid):
    # file_path = os.path.join("val", fileid)
    if flask.request.method == 'GET':
        val = s.GetValue(fileid)
        if not val:
            return flask.abort(404)
        binary = pickle.dumps(val)
        return binary, 200
    else:
        flask.request.get_data()
        val = pickle.loads(flask.request.data)
        session.make_transient(val)
        print("--------------store value to DB---------------")
        s.StoreValues([val, ])
        print(
            "-----------------successfully stored duplicate value to DB ---------------")
        s.PushValues()
        context = {
            "id": fileid,
            "value": "received"
        }
        return flask.jsonify(**context), 201


@app.route("/var/<varname>", methods=['GET', 'POST'])
def ReturnVariable(varname):
    if flask.request.method == 'GET':
        print("-----------------get var/varname------------------")
        # if s.serverURL:
        #     var = s.GetVariable(varname)
        #     binary = pickle.dumps(var)
        #     return binary, 200
        var = s.GetVariable(varname)
        if not var:
            return flask.abort(404)
        binary = pickle.dumps(var)
        return binary, 200
    else:
        print("-----------------post var/varname------------------")

        flask.request.get_data()
        var = pickle.loads(flask.request.data)
        s.SetVariable(var)
        context = {
            "variable": "set"
        }
        return flask.jsonify(**context), 201


@app.route("/var", methods=['POST'])
def RegisterVariable():
    print("----------------post /var-------------------")
    flask.request.get_data()
    var = pickle.loads(flask.request.data)
    # if s.serverURL:  # currently dont have parent
    #     return s.RegisterVariable(var)
    # session.make_transient(var)
    s.RegisterVariable(var)
    # s.PushValues()
    context = {
        "var_id": var.id,
        "value": "registered"
    }
    return flask.jsonify(**context), 201


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()

# @app.route("/var/<fileid>", methods=['GET', 'PUT'])
# def ReturnVariable(fileid):
#     # file_path = os.path.join("var", fileid)
#     if flask.request.method == 'GET':
#         var = s.GetVariable(fileid)
#         if not var:
#             return flask.abort(404)
#         else:
#             context = {"var": jsonpickle.encode(var)}
#             return flask.jsonify(**context), 200
#     else:
#         timestamp = flask.request.json["timestamp"]
#         val = jsonpickle.decode(flask.request.json["value"])
#         # var = s.SetVariable(fileid, val, timestamp) TODO: fix it
#         # if not var:
#         #     return flask.abort(404)
#         # context = {
#         #     "var": jsonpickle.encode(var)
#         # }
#         context = {
#             "place": "holder"
#         }
#         return flask.jsonify(**context), 201

# @app.route("/var", methods=['POST'])
# def RegisterVariable():
#     data = flask.request.json
#     print(data)
#     value = jsonpickle.decode(data["value"])
#     timestamp = data["timestamp"]
#     filename = s.RegisterVariable(value, timestamp)
#     path = os.path.join("var", filename)
#     infile = open(path, "r")
#     context = {
#         "varName": filename,
#         "var": infile.read()
#     }
#     infile.close()
#     return flask.jsonify(**context), 201
