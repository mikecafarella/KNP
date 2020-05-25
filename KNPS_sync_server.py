import flask
import os
import pickle
import json
import jsonpickle
from kgpl import KGPLValue, KGPLVariable


app = flask.Flask(__name__)
if not os.path.exists("val/"):
  os.mkdir("val/")
if not os.path.exists("var/"):
  os.mkdir("var/")

@app.route("/val/<fileid>", methods=['GET', 'POST'])
def ReturnValue(fileid):
  file_path = os.path.join("val", fileid)
  if flask.request.method == 'GET':
    try:
      return flask.send_file(os.path.abspath(file_path),as_attachment = True)
    except FileNotFoundError:
      return flask.abort(404)
  else:
    flask.request.files["file"].save(file_path)
    infile = open(file_path, "rb")
    val = pickle.load(infile)
    infile.close()
    context = {
        "id" : fileid,
        "value" : val.__repr__()
      }
    return flask.jsonify(**context), 201

@app.route("/var/<fileid>", methods=['GET', 'PUT'])
def ReturnVariable(fileid):
  file_path = os.path.join("var", fileid)
  if flask.request.method == 'GET':
    try:
      return flask.send_file(os.path.abspath(file_path),as_attachment = True)
    except FileNotFoundError:
      return flask.abort(404)
  else:
    # to do
    flask.request.files["file"].save(file_path)
    infile = open(file_path, "rb")
    var = pickle.load(infile)
    infile.close()
    context = {
        "id" : fileid,
        "value" : var.__repr__()
      }
    return flask.jsonify(**context), 201

@app.route("/var", methods=['POST'])
def RegisterVariable():
  data = flask.request.json
  print(data)
  variable = data["variable"]
  variable = jsonpickle.decode(variable)
  varNumFile = os.path.join("var", "maxVar")
  if not os.path.exists(varNumFile):
    outfile = open(varNumFile, "w")
    outfile.write("1")
    outfile.close()
    filename = "K0"
  else:
    infile = open(varNumFile, "r")
    num = infile.readline()
    infile.close()
    filename = "K"+num
    nextNum = int(num) + 1
    outfile = open(varNumFile, "w")
    outfile.write(str(nextNum))
    outfile.close()
  variable.varName = filename
  outfile = open(os.path.join("var",filename), "w")
  outfile.write(jsonpickle.encode(variable))
  outfile.close()
  context = {"varName": filename}
  return flask.jsonify(**context), 201
  
