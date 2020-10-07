import json
import os
import pandas

import requests
import ORM_modified as ORM

# server_url = "http://lasagna.eecs.umich.edu:8000/"
# server_url = "http://lasagna.eecs.umich.edu:5000"
server_url = "http://127.0.0.1:5000"
next_val_id_url = server_url + "/nextval"
next_var_id_url = server_url + "/nextvar"

val_url = server_url + "/val"
var_url = server_url + "/var"
loadvar_url = server_url + "/load/var"
loadval_url = server_url + "/load/val"
update_url = server_url + "/getLatest"
download_url = server_url + "/uploads"



class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, KGPLValue):
            return {"vid": obj.vid, "__kgplvalue__": True}
        elif isinstance(obj, KGPLVariable):
            return {"vid": obj.vid, "__kgplvariable__": True}
        elif isinstance(obj, ORM.Relation):
            return {
                "entity_id": obj.entity_id,
                "query_str": obj.query_str,
                "dic": obj.dic,
                "result_dic": obj.result_dic,
                "df": obj.df.to_json(),
                "count": obj.count,
                "time_property": obj.time_property,
                "time": obj.time,
                "limit": obj.limit,
                "focus": obj.focus,
                "__relation__": True
            }
        elif isinstance(obj, Image):
            return {"filename": obj.filename, "__image__": True}
        return json.JSONEncoder.default(self, obj)



def hook(dct):
    if "__kgplvalue__" in dct:
        return load_val(dct["vid"])
    elif "__kgplvariable__" in dct:
        return load_var(dct["vid"])
    elif "__relation__" in dct:
        #  entity_id: str, property_id: str, isSubject: bool, limit: int, rowVerbose: bool,
        #  colVerbose: bool, time_property: str, time: str, name: str, reconstruct={}):
        dct["df"] = pandas.read_json(dct["df"])
        temp_dict = {}
        # dct["dic"] is a dict with integer keys.
        for k,v in dct["dic"].items():
            try:
                key = int(k)
                temp_dict[key] = dct["dic"][k]
            except Exception:
                print("Count should be an integer")
        dct["dic"] = temp_dict
        return ORM.Relation("dummy", "dummy,", False, 42, False, False, "dummy", "dummy", "dummy", dct)
    elif "__image__" in dct:
        return Image(dct["filename"])
    return dct


class Image:
    def __init__(self, filename):
        self.filename = filename


class KGPLValue:
    def __init__(self, val, comment, user="anonymous", dependency=[], vid=None, verbose=False):
        if vid is None:
            # generate a new kgplValue
            # self.ID = get id from server
            # r = requests.get(next_val_id_url)
            self.val = val
            self.comment = comment
            for i, d in enumerate(dependency):
                if isinstance(d, KGPLValue):
                    dependency[i] = d.getVid()
                elif isinstance(d, KGPLVariable):
                    dependency[i] = d.getValid()
                elif not isinstance(d, str):
                    raise Exception("dependency list not valid")
            self.dependency = dependency
            self.user = user
            """
            if r.status_code == 200:
                self.vid = r.json()["id"]
            else:
                raise Exception("not getting correct id")
            """
            # if this is a picture/pdf/other files
            val_json = val.to_json() if isinstance(
                val, pandas.DataFrame) else json.dumps(val, cls=MyEncoder)
            if isinstance(val, Image):
                r = requests.post(val_url, data={
                                             "val": val_json,
                                             "pyType": type(val).__name__,
                                             "comment": comment,
                                             "user": user, "dependency": json.dumps(dependency)},
                                           files = { "file": open(val.filename, "rb") }) 
            else:               
                r = requests.post(val_url, data={
                                             "val": val_json,
                                             "pyType": type(val).__name__,
                                             "comment": comment,
                                             "user": user, "dependency": json.dumps(dependency)},)
            if r.status_code == 201:
                self.vid = r.json()["url"]
                if verbose:
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
        if type(self.val) in [int, str, float, pandas.DataFrame]:
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
        elif type(self.val) is ORM.Relation:
            return str(self.val)
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
            # r = requests.get(next_var_id_url)
            """
            if r.status_code == 200:
                self.vid = r.json()["id"]
                print("Created KGPLVariable with ID", self.vid,
                      "$ KGPLValue with ID:", self.val_id)
            else:
                raise Exception("not getting correct id")
            """
            r = requests.post(var_url,
                              json={"val_id": self.val_id,
                                    "comment": comment, "user": user})
            if r.status_code != 201:
                if r.status_code == 404:
                    print("value id not found")
                raise Exception("creation failed")
            ts = r.json().get("timestamp")
            url = r.json()["url"]
            self.timestamp = ts
            self.vid = url
        else:
            # generate an existing kgplVariable
            # never use this method
            self.vid = vid
            self.val_id = val_id
            # should always initialzie the value of self.timestamp afterwards.
            self.timestamp = timestamp

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


def value(val, comment, user="anonymous", dependency=[], verbose=False):
    if type(val) not in [int, float, tuple, list, dict, str, KGPLValue,
                         KGPLVariable, pandas.DataFrame, ORM.Relation, Image]:
        raise Exception("cannot construct KGPLValue on this type")
    if type(comment) != str:
        raise Exception("Comment needs to be a string.")
    if type(dependency) != list:
        raise Exception("Dependency must be a list of url.")
    if type(user) != str:
        raise Exception("user name must be a string.")
    return KGPLValue(val, comment, user, dependency, verbose=verbose)


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
    elif context["pyt"] == 'Image':
        r = requests.get(os.path.join(download_url, str(vid[vid.rfind('/') + 1:])))
        if "filename" not in context["val"]:
            raise Exception("filename isn't returned by server")
        if r.status_code != 200:
            raise Exception("file cannot be download") 
        open(tmp_val.filename, "wb").write(r.content)
        val = tmp_val
    elif context["pyt"] == 'DataFrame':
        val = pandas.read_json(context["val"])
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
