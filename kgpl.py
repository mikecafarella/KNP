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

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, KGPLValue): 
            return {"vid": obj.vid, "__kgplvalue__": True}
        elif isinstance(obj, KGPLVariable):
            return {"vid": obj.vid, "__kgplvariable__": True}
        return json.JSONEncoder.default(self, obj)

def hook(dct):
    if "__kgplvalue__" in dct:
        return load_val(dct["vid"])
    elif "__kgplvariable__" in dct:
        return load_var(dct["vid"])
    return dct

class KGPLValue:
    def __init__(self, val, vid=None):
        if vid is None:
            # generate a new kgplValue
            # self.ID = get id from server
            r = requests.get(next_id_url)
            if r.status_code == 200:
                self.vid = r.json()["id"]
            else:
                raise Exception("not getting correct id")

            r = requests.post(val_url, json={"id": self.vid, "val": json.dumps(val, cls=MyEncoder), "pyType": type(val).__name__})
            if r.status_code == 201:
                self.val = val
            else:
                raise Exception("creation failed")
        else:
            # generate an existing kgplValue
            self.vid = vid
            self.val = val

    def getVid(self):
        return self.vid
    
    def getConcreteVal(self):
        return self.val

    def __repr__(self):
        if type(self.val) in [int, str, float]:
            return self.val.__repr__()
        elif type(self.val) in [list, tuple]:
            rst = []
            for x in self.val:
                if type(x) is KGPLValue:
                    rst.append("KGPLValue with ID:" + str(x.vid))
                else:
                    rst.append(x.__repr__())
            if type(self.val) is tuple:
                return str(tuple(rst))
            return str(rst)
        elif type(self.val) is dict:
            rst = {}
            for k in self.val:
                v = self.val[k]
                if type(v) is KGPLValue:
                    rst[k] = "KGPLValue with ID:" + str(v.vid)
                else:
                    rst[k] = v.__repr__()
            return str(rst)
        elif type(self.val) is KGPLValue:
            rst = "KGPLValue with ID:" + str(self.val.vid)
            return str(rst)
        else:
            raise Exception("val type invalid")

class KGPLVariable:
    def __init__(self, val_id, vid=None, timestamp=None):
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
            ts = r.json().get("timestamp")
            self.timestamp = ts
        else:
            # generate an existing kgplVariable
            self.vid = vid
            self.val_id = val_id
            self.timestamp = timestamp # should always initialzie the value of self.timestamp afterwards.
    
    def getVid(self):
        return self.vid
    """
    to do:
    def getValid(self):
    """

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
    if type(val) not in [int, float, tuple, list, dict, str, KGPLValue, KGPLVariable]:
        raise Exception("cannot construct KGPLValue on this type")
    return KGPLValue(val)

def variable(val_id):
    # val_id is the id of the kgplValue this variable should point to.
    return KGPLVariable(val_id)

def load_val(vid):
    context = load(vid, loadval_url)
    tmp_val = json.loads(context["val"], object_hook=hook)
    if context["pyt"] == 'tuple':
        val = tuple(tmp_val)
    else:
        val = tmp_val
    return KGPLValue(val, vid)

def load_var(vid):
    context = load(vid, loadvar_url)
    return KGPLVariable(context["val_id"], vid, context["timestamp"])

def get_val_of_var(kg_var):
    concrete_val = load_val(kg_var.val_id)
    print(concrete_val.__dict__)

def set_var(kg_var, val_id):
    """
    vg_var is the kgplVariable.
    val_id is the id of the kgplValue it should point to.
    Return the updated kgplVariable.
    """
    r = requests.put(var_url, json={"vid": kg_var.vid, "val_id": val_id, "timestamp": kg_var.timestamp})
    if r.status_code != 201:
        if r.status_code == 404:
            print("variable not found")
        elif r.status_code == 403:
            print("version conflict")
        raise Exception("variable updating not success")
    kg_var.timestamp = r.json().get("timestamp")
    kg_var.val_id = val_id
    return kg_var

def get_history(kg_var):
    r = requests.get(os.path.join(server_url, "gethistory"), json={"vid": kg_var.vid})
    if r.status_code != 200:
        raise Exception("getting history failed")
    l = r.json()["list"]
    return l