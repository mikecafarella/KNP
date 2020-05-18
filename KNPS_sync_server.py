import flask
import os
import pickle
from kgpl import KGPLValue, KGPLVariable


app = flask.Flask(__name__)
if not os.path.exists("/val/"):
  os.mkdir("/val/")


@app.route("/val/<fileid>", methods=['GET', 'POST'])
def ReturnValue(fileid):
  file_path = os.path.join("/val", fileid)
  if flask.request.method == 'GET':
    if os.path.exists(file_path):
      infile = open(file_path, "rb")
      val = pickle.load(infile)
      infile.close()
      return val
    else: 
      return "no value found"
      
      #TODO: value not found
  else:
    flask.request.files["file"].save("a")
    outfile = open("a", "rb")
    val = pickle.load(outfile)
    print(val.__repr__())
    outfile.close()
    return "post received"
