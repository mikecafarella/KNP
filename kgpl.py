import requests
import json
import os

server_url = "http://lasagna.eecs.umich.edu:80"
next_id_url = server_url + "/next"
val_url = server_url + "/val"

load_url = server_url + "/load"

class KGPLValue:
    def __init__(self, val, id=None):
        if id is None:
            # self.ID = get id from server
            r = requests.get(next_id_url)
            if r.status_code == 200:
                self.ID = json.loads(r.text)
            else:
                raise Exception("not getting correct id")

            r = requests.post(val_url, json=json.dumps(val))
            if r.status_code == 201:
                self.val = val
            else:
                raise Exception("created failed")
        else:
            self.ID = id
            self.val = val

class KGPLVariable:
    def __init__(self, val_id):
        self.ID = None
        
        # if valid
        self.points_to = val_id
    


def value(val):
    return KGPLValue(val)

def variable(val_id):
    return KGPLVariable(val_id)

def load(id):
    r = requests.get(os.path.join(load_url, str(id)))
    if r.status_code != 200:
        raise Exception("value not found")
    return KGPLValue(json.loads(r.text), id)




    
