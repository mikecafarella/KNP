import json
import os

import requests

# server_url = "http://lasagna.eecs.umich.edu:8000/"
server_url = "http://127.0.0.1:5000"
next_val_id_url = server_url + "/nextval"
next_var_id_url = server_url + "/nextvar"

val_url = server_url + "/val"
var_url = server_url + "/var"
loadvar_url = server_url + "/load/var"
loadval_url = server_url + "/load/val"
update_url = server_url + "/getLatest"
upload_url = server_url + "/upload"

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


def upload_file(filename, value_id):
    with open(filename, 'rb') as img:
        vid = value_id.split("/")[-1]
        # print(vid)
        name_img= os.path.basename(filename)
        file_to_upload = {
            'file': open(name_img,'rb'),
            "value_id": open(str(vid),'w+')
        }
        os.remove(str(vid))
        r = requests.post(upload_url, files=file_to_upload)
        return r.json()["filename_stored"]

class KGPLValue:
    def __init__(self, val, comment, user="anonymous", dependency=[], vid=None):
        if vid is None:
            # generate a new kgplValue
            # self.ID = get id from server
            r = requests.get(next_val_id_url)
            self.val = val
            self.comment = comment
            for i,d in enumerate(dependency):
                if isinstance(d, KGPLValue):
                    dependency[i] = d.getVid()
                elif isinstance(d, KGPLVariable):
                    dependency[i] = d.getValid()
                elif not isinstance(d, str):
                    raise Exception("dependency list not valid")
            self.dependency = dependency
            self.user = user
            if r.status_code == 200:
                self.vid = r.json()["id"]
            else:
                raise Exception("not getting correct id")
            
            
            #if this is a picture/pdf/other files
            if isinstance(val,dict):
                if "__file__" in val.keys():
                    # if val["__file__"] is "pic":
                    stored_file_name = upload_file(val["original_name"], self.vid)
                    val["stored_name"] = stored_file_name

            
            r = requests.post(val_url, json={"id": self.vid,
                                            "val": json.dumps(val,
                                                                cls=MyEncoder),
                                            "pyType": type(val).__name__,
                                            "comment": json.dumps(comment,
                                                                    cls=MyEncoder),
                                            "user": user, "dependency": dependency},)
            if r.status_code == 201:
                print("Created: KGPLValue with ID", self.vid, "$", self)
            else:
                raise Exception("creation failed")
        else:
            # generate an existing kgplValue
            # never use this method
            self.vid = vid
            self.val = val
            self.comment = comment

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
    def __init__(self, val_id, comment, user="anonymous", vid=None, timestamp=None):
        self.val_id = val_id
        self.comment = comment
        self.user = user
        if not vid:
            # generate a new kgplVariable
            # self.ID = get id from server
            r = requests.get(next_var_id_url)
            if r.status_code == 200:
                self.vid = r.json()["id"]
                print("Created KGPLVariable with ID", self.vid,
                      "$ KGPLValue with ID:", self.val_id)
            else:
                raise Exception("not getting correct id")

            r = requests.post(var_url,
                              json={"id": self.vid, "val_id": self.val_id,
                                    "comment": comment, "user": user})
            if r.status_code != 201:
                if r.status_code == 404:
                    print("value id not found")
                raise Exception("creation failed")
            ts = r.json().get("timestamp")
            self.timestamp = ts
        else:
            # generate an existing kgplVariable
            # never use this method
            self.vid = vid
            self.val_id = val_id
            self.timestamp = timestamp  # should always initialzie the value of self.timestamp afterwards.

    def getVid(self):
        return self.vid

    def getValid(self):
        return self.val_id

    def refresh(self):
        r = requests.get(update_url, json={"val_id": self.vid})
        if r.status_code != 200:
            raise Exception("fail to get latest information")
        self.val_id = r.json().get("val_id")
        self.timestamp = r.json().get("timestamp")

    def getConcreteVal(self):
        return load_val(self.val_id)

def load(vid, l_url):
    par = {"vid": vid}
    r = requests.get(l_url, params=par)
    if r.status_code != 200:
        raise Exception("value or variable not found")
    context = r.json()
    return context


# ---------------------------API-----------------------------------#


def value(val, comment, user="anonymous", dependency=[]):
    if type(val) not in [int, float, tuple, list, dict, str, KGPLValue,
                         KGPLVariable]:
        raise Exception("cannot construct KGPLValue on this type")
    if type(comment) != str:
        raise Exception("Comment needs to be a string.")
    if type(dependency) != list:
        raise Exception("Dependency must be a list of url.")
    if type(user) != str:
        raise Exception("user name must be a string.")
    return KGPLValue(val, comment, user, dependency)


def variable(val_id, comment, user="anonymous"):
    if type(val_id) not in [str, KGPLValue]:
        raise Exception("cannot construct KGPLVariable")
    if type(val_id) is KGPLValue:
        val_id = val_id.getVid()
    if type(comment) != str:
        raise Exception("Comment needs to be a string.")
    return KGPLVariable(val_id, comment, user)


def load_val(vid):
    context = load(vid, loadval_url)
    tmp_val = json.loads(context["val"], object_hook=hook)

    if context["pyt"] == 'tuple':
        val = tuple(tmp_val)
    elif context["pyt"] == 'dict':
        if 
        val = {
            "filename": tmp_val["original_name"],
            "type": tmp_val["__file__"]
            }
        r = requests.get(upload_url+"s/"+tmp_val["stored_name"])
        if r.status_code!=200:
            raise Exception("file cannot be download")
        open(tmp_val["original_name"],'wb').write(r.content)
    else:
        val = tmp_val
    return KGPLValue(val, context["comment"], context["user"], context["dependency"], vid)


def load_var(vid):
    context = load(vid, loadvar_url)
    return KGPLVariable(context["val_id"], context["comment"], context["user"], vid,
                        context["timestamp"])

# to do: ask if set_var change the owner of the variable?
def set_var(kg_var, val_id, new_comment):
    """
    kg_var is the kgplVariable.
    val_id is the id of the kgplValue it should point to.
    Return the updated kgplVariable.
    """
    r = requests.put(var_url, json={"vid": kg_var.vid, "val_id": val_id,
                                    "timestamp": kg_var.timestamp,
                                    "new_comment": new_comment})
    if r.status_code != 201:
        if r.status_code == 404:
            print("variable not found")
        elif r.status_code == 403:
            print("version conflict")
        raise Exception("variable updating not success")
    kg_var.timestamp = r.json().get("timestamp")
    kg_var.val_id = val_id
    kg_var.comment = new_comment
    print("KGPLVariable", kg_var.vid, "Updated.", "New val_id:", kg_var.val_id)
    return kg_var


def get_history(kg_var):
    r = requests.get(os.path.join(server_url, "gethistory"),
                     json={"vid": kg_var.vid})
    if r.status_code != 200:
        raise Exception("getting history failed")
    l = r.json()["list"]
    return l


def changeNamespace(new_url):
    global server_url
    print("Old Server: ", server_url)
    new_url = new_url.rstrip('/')
    server_url = new_url
    print("New Server: ", server_url)
    return new_url


def viewNamespace():
    print("Current Server: ", server_url)
    return server_url
