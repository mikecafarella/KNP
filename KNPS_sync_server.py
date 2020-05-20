import flask
import os
import pickle
from kgpl import KGPLValue, KGPLVariable


app = flask.Flask(__name__)
if not os.path.exists("val/"):
  os.mkdir("val/")


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

@app.route("/var/<fileid>", methods=['GET', 'POST'])
def ReturnVariable(fileid):
  file_path = os.path.join("var", fileid)
  if flask.request.method == 'GET':
    try:
      return flask.send_file(os.path.abspath(file_path),as_attachment = True)
    except FileNotFoundError:
      return flask.abort(404)
  else:
    flask.request.files["file"].save(file_path)
    infile = open(file_path, "rb")
    var = pickle.load(infile)
    infile.close()
    context = {
        "id" : fileid,
        "value" : var.__repr__()
      }
    return flask.jsonify(**context), 201