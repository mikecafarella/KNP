import requests
import time
import json
import os

server_url = "http://127.0.0.1:5000"
next_id_url = server_url + "/next"
val_url = server_url + "/val"
var_url = server_url + "/var"
loadvar_url = server_url + "/load/var"
loadval_url = server_url + "/load/val"

class KGPLValue:
    def __init__(self, val, vid=None, timestamp=None):
        if vid is None:
            # generate a new kgplValue
            # self.ID = get id from server
            r = requests.get(next_id_url)
            if r.status_code == 200:
                self.vid = r.json()["id"]
            else:
                raise Exception("not getting correct id")

            r = requests.post(val_url, json={"id": self.vid, "val": val, "pyType": type(val).__name__, "timestamp": time.time()})
            if r.status_code == 201:
                self.val = val
                self.timestamp = r.json().get("timestamp")
            else:
                raise Exception("creation failed")
        else:
            # generate an existing kgplValue
            self.vid = vid
            self.val = val
            self.timestamp = timestamp

class KGPLVariable:
    def __init__(self, val_id, vid=None):
        self.val_id = val_id
        if not vid:
            # generate a new kgplVariable
            # self.ID = get id from server
            r = requests.get(next_id_url)
            if r.status_code == 200:
                self.vid = r.json()["id"]
            else:
                raise Exception("not getting correct id")

            r = requests.post(var_url, json={"id": self.vid, "val_id": self.val_id})
            if r.status_code != 201:
                if r.status_code == 404:
                    print("value id not found")
                raise Exception("creation failed")
        else:
            # generate an existing kgplVariable
            self.vid = vid
            self.val_id = val_id


def load(vid, l_url):
    r = requests.get(os.path.join(l_url, str(vid)))
    if r.status_code != 200:
        raise Exception("value or variable not found")
    context = r.json()
    return context
    

"""
Users should only use the following functions for safety
"""
def value(val):
    return KGPLValue(val)

def variable(val_id):
    # val_id is the id of the kgplValue this variable should point to.
    return KGPLVariable(val_id)

def load_val(vid):
    context = load(vid, loadval_url)
    if context["pyt"] == 'tuple':
        val = tuple(context["val"])
    else:
        val = context["val"]
    return KGPLValue(val, vid, context["timestamp"])

def load_var(vid):
    context = load(vid, loadvar_url)
    return KGPLVariable(context["val_id"], vid)

def set_var(vid, val_id):
    """
    vid is the id of the kgplVariable.
    val_id is the id of the kgplValue it should point to.
    Return the updated kgplVariable.
    """
    r = requests.put(var_url, json={"vid": vid, "val_id": val_id})
    if r.status_code != 201:
        if r.status_code == 404:
            print("variable not found")
        raise Exception("variable updating not success")
    return KGPLVariable(val_id, vid)



    




    
