import requests
import json
import os

server_url = "http://lasagna.eecs.umich.edu:80"
next_id_url = server_url + "/next"
val_url = server_url + "/val"
var_url = server_url + "/var"
loadvar_url = server_url + "/load/var"
loadval_url = server_url + "/load/val"

class KGPLValue:
    def __init__(self, val, vid=None, timestamp=None):
        if id is None:
            # self.ID = get id from server
            r = requests.get(next_id_url)
            if r.status_code == 200:
                self.vid = json.loads(r.text)
            else:
                raise Exception("not getting correct id")

            r = requests.post(val_url, json={"id": self.vid, "val": val, "pyType": type(val).__name__, "timestamp": time.time()})
            # to do: return timestamp
            if r.status_code == 201:
                self.val = val
                self.timestamp = r.json().get("timestamp")
            else:
                raise Exception("creation failed")
        else:
            self.vid = id
            self.val = val
            self.timestamp = timestamp

class KGPLVariable:
    def __init__(self, val_id, vid=None):
        self.vid = None
        
    


def value(val):
    return KGPLValue(val)

def variable(val_id):
    return KGPLVariable(val_id)

def load_val(vid):
    load(vid, loadval_url)

def load_var(vid):
    load(vid, loadvar_url)

def load(vid, l_url):
    r = requests.get(os.path.join(l_url, str(id)))
    if r.status_code != 200:
        raise Exception("value not found")
    context = r.json()
    if context["pyt"] == 'tuple':
        val = tuple(context["val"])
    else:
        val = context["val"]
    return KGPLValue(val, vid, context["timestamp"])




    
