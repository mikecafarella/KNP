from gen import ID_gen
import flask
import os

app = flask.Flask(__name__)

server_url = "http://lasagna.eecs.umich.edu:80"
next_id_url = server_url + "/next"
val_url = server_url + "/val"
load_url = server_url + "/load"

@app.route("/next", methods=['GET'])
def return_id():
    id = ID_gen.next()
    context = {   
        "id": id
    }
    return flask.jsonify(**context), 200

#@app.route(os.path.join(load_url, "<id>"), methods=['GET'])
#def return_val_or_var(id):
