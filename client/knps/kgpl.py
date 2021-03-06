import json
import os
import pandas
import dill
import pickle
import marshal
import base64
import types

import requests
from .func_storage import *
from . import ORM_client as ORM
from .settings import SERVER_URL

server_url = SERVER_URL
# server_url = "http://lasagna.eecs.umich.edu:8000"
# server_url = "http://lasagna.eecs.umich.edu:5000"
# server_url = "http://127.0.0.1:5000"
next_val_id_url = server_url + "/nextval"
next_var_id_url = server_url + "/nextvar"

val_url = server_url + "/val"
var_url = server_url + "/var"
loadvar_url = server_url + "/load/var"
loadval_url = server_url + "/load/val"
update_url = server_url + "/getLatest"
download_url = server_url + "/static/uploads"
check_var_id_url = server_url + "/checkvarid"


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
                "subclass":obj.subclass,
                "focus": obj.focus,
                "__relation__": True
            }
        elif isinstance(obj, File):
            return {"filename": obj.filename, "__image__": True}
        if (isinstance(obj, FunctionWithSignature)):
            type_list = []
            for t in obj.typeSignature:
                encoded_obj = base64.b64encode(dill.dumps(t))
                type_list.append(encoded_obj.decode('ascii'))
            encoded_code = base64.b64encode(marshal.dumps(obj.fn.__code__))
            encoded_defaults = base64.b64encode(
                pickle.dumps(obj.fn.__defaults__))
            encoded_closure = base64.b64encode(
                pickle.dumps(obj.fn.__closure__))
            return {
                "types": type_list,
                "__funcwithsig__": True,
                "code": encoded_code.decode('ascii'),
                "defaults": encoded_defaults.decode('ascii'),
                "closure": encoded_closure.decode('ascii')
            }
        
        return json.JSONEncoder.default(self, obj)


def hook(dct):
    if "__kgplvalue__" in dct:
        return load_val(dct["vid"])
    elif "__kgplvariable__" in dct:
        return load_var(dct["vid"])
    elif "__relation__" in dct:
    # def __init__(self, entity_id: str, property_id: str, isSubject: bool, rowVerbose: bool,
    #              colVerbose: bool, time_property: str, time: str, name: str, label: bool, 
    #              limit=10000, subclass=False, showid=False, reconstruct={}):
        dct["df"] = pandas.read_json(dct["df"])
        temp_dict = {}
        # dct["dic"] is a dict with integer keys.
        for k, v in dct["dic"].items():
            try:
                key = int(k)
                temp_dict[key] = dct["dic"][k]
            except Exception:
                print("Count should be an integer")
        dct["dic"] = temp_dict
        return ORM.Relation("dummy", "dummy,", False, False, False, "dummy", "dummy", "dummy",
                            False,10000,False, False, dct)
    elif "__image__" in dct:
        return File(dct["filename"])
    elif "__funcwithsig__" in dct:
        type_list = []
        for t in dct["types"]:
            decode_type = base64.b64decode(t)
            type_list.append(dill.loads(decode_type))

        decoded_code = base64.b64decode(dct["code"])
        decoded_defaults = base64.b64decode(dct["defaults"])
        decoded_closure = base64.b64decode(dct["closure"])

        marshaled_func = marshal.loads(decoded_code)
        pickled_arguments = pickle.loads(decoded_defaults)
        pickled_closure = pickle.loads(decoded_closure)

        fn = types.FunctionType(marshaled_func, globals(),
                                "funcname", pickled_arguments, pickled_closure)

        return FunctionWithSignature(fn, type_list)
    return dct


class File:
    """
    File wrapper class. This wrapper class should be used when storing a file into a KGPLValue object.

    ###### Parameters
    - `filename`
        The absolute or relative path to the file .
    
    ###### Example

            import knps
            file = knps.File("picture.png")
            kgplvalue = knps.create_values(file, "a picture")

    """
    def __init__(self, filename):
        self.filename = filename


class KGPLValue:
    """
    Python representation of a KGPLValue. Users should not user the constructor to create a KGPLValue object directly. Instead, use the `create_value` function described below.

    ###### Parameters
    - `val`
        The concrete value stored in the KGPLValue object.
    - `comment`
        A user-readable comment (of type `str`) associated with this KGPLValue object.
    - `user`
        Username of the owner of the KGPLValue object.
    - `dependency`
        A list consisting of the KGPL objects that this KGPLValue depended on. 
    - `vid`
        The unique identifier assigned by the server.
    - `verbose`
        If set to true, more information is produced in the terminal. Otherwise, a succint description is printed when the construction succeeds.

    """
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
            # """
            # if r.status_code == 200:
            #     self.vid = r.json()["id"]
            # else:
            #     raise Exception("not getting correct id")
            # """
            # if this is a picture/pdf/other files
            val_json = val.to_json() if isinstance(
                val, pandas.DataFrame) else json.dumps(val, cls=MyEncoder)
            if isinstance(val, File):
                r = requests.post(val_url, data={
                    "val": val_json,
                    "pyType": type(val).__name__,
                    "comment": comment,
                    "user": user,
                    "dependency": json.dumps(dependency)},
                    files={"file": open(val.filename, "rb")})
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
                    print("Created: KGPLValue with ID", self.vid)
            else:
                raise Exception("creation failed")

        else:
            # generate an existing kgplValue
            # never use this method
            self.vid = vid
            self.val = val
            self.comment = comment
            self.user = user
            self.dependency = dependency

    def getVid(self):
        """
        Return the vid
        """
        return self.vid

    def getConcreteVal(self):
        """
        Return the concrete value
        """
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

    def create_label(self, label, comment):
        """
        Create a label to refer to this KGPLValue. 

        ###### Parameters
        - `label`
            A label (of type `str`) identifier for the value. Consider use label as a 
        - `comment`
            Descriptive comment for the label creation

        ###### Return
        The KGPLVariable object that underlies the label
        """
        return variable(label, self.vid, comment, user=self.user)

    def update_label(self, label, new_comment):
        """
        Update the input label with this KGPLValue
        
        ###### Parameters
        - `label`
            The label to be updated
        - `comment`
            Descriptive comment for the label update

        ###### Return
        The KGPLVariable object that underlies the label
        """

        temp = load_var(server_url+"/var/"+label)
        return set_var(temp, self.vid, new_comment)

def check_label_occupied(vid):
    """
    Check the server to determine if the label is occupied.

    ###### Parameter
    - `vid`
        The label name to check
    """
    r = requests.post(check_var_id_url, json={"var_id": vid})
    if r.status_code != 201:
        if r.status_code == 409:
            raise Exception("var id occupied")
        else:
            raise Exception("unknown error, aborting...")

def get_default_label():
    r = requests.get(next_var_id_url)
    if r.status_code != 201:
        raise Exception("unknown error when get default label, aborting...")
    else:
        return r.json()["id"]

class KGPLVariable:
    """
    Python representation of a KGPLVariable. Users should not user the constructor to create a KGPLVariable object directly. Instead, use the `variable` function described below.

    ###### Parameters
    - `val_id`
        The vid of the KGPLValue to be stored
    - `comment`
        A user-readable comment (of type `str`) associated with this KGPLVariable object.
    - `vid`
       The unique identifier assigned by the server.
    - `user`
        Username of the owner of the KGPLVariable object.
    - `timestamp`
        Timestamp of the variable creation

    """
    def __init__(self, val_id, comment, vid, user="anonymous", timestamp=None):
        self.val_id = val_id
        self.comment = comment
        self.user = user
        if not timestamp:  # generate a new kgplVariable
            # check_label_occupied() # No need to check because the API check!!! If API change, it needs to check
            r = requests.post(var_url,
                              json={"val_id": self.val_id, "var_id": vid,
                                    "comment": comment, "user": user})
            if r.status_code != 201:
                if r.status_code == 404:
                    raise Exception("value id not found")
                raise Exception("variable creation failed with unknown error")
            ts = r.json().get("timestamp")
            url = r.json()["url"]
            self.timestamp = ts
            self.vid = url
            print("Created: KGPLVariable with ID", self.vid)
        else:
            # generate an existing kgplVariable for load_var
            self.vid = vid
            self.timestamp = timestamp

    def getVid(self):
        """
        Get the vid
        ###### Return
        - the vid of this KGPLVariable.
        """
        return self.vid

    def getValid(self):
        """
        Get the vid of the contained KGPLValue
        ###### Return
        - the vid of the KGPLValue this variable refers to.
        """
        return self.val_id

    def refresh(self):
        """
        Synchronize with the server to get the newest state of the variable in case of users work on the same 
        variable concurrently.
        """
        r = requests.get(update_url, json={"val_id": self.vid})
        if r.status_code != 200:
            raise Exception("fail to get latest information")
        self.val_id = r.json().get("val_id")
        self.timestamp = r.json().get("timestamp")

    def getConcreteVal(self):
        """
        Get the KGPLValue stored in this KGPLVariable object

        ###### Return
            - The KGPLValue object stored in this variable
        """
        return load_val(self.val_id)


def load(vid, l_url):
    par = {"vid": vid}
    # print(vid)
    # print(l_url)
    r = requests.get(l_url, params=par)
    if r.status_code != 200:
        raise Exception("value or variable not found")
    context = r.json()
    return context


# ---------------------------API-----------------------------------#

def create_value(val, comment, user="anonymous", dependency=[], verbose=False):
    """
    Create a KGPLValue based on the inputs and publish to the server.

    ###### Parameter
    - 'val'
        Concrete value to store (We currently support the following types: `int`, `float`, `bool`, `list`, `dict`, `File`, `pandas.DataFrame`, `Relation`)
    - 'comment'
        A human readable comment (of type `str`) associated with the value creattion
    - 'user'
        User name of the owner of the KGPLValue, the default value is `anonymous`
    - `dependency`
        A list consisting of the KGPL objects that this KGPLValue depended on. Each element in the list can be one of the three types:
        `KGPLValue`, `KGPLVariable` or `Label`. The default value is empty list.
    - `verbose`: 
        If set to true, more information is produced in the terminal. Otherwise, a succint description is printed when the construction succeeds. The default value is `False`.

    ###### Return
    A KGPLValue object constructed based on inputs
    """
    # dependency list can be KGPLValue/KGPLVariable/Label
    refined_dependency = []
    for d in dependency:
        if d not in [KGPLValue, KGPLVariable]:
            if type(d)!= str:
                raise Exception("dependency list can only be KGPLValue/KGPLVariable/Label")
            else:
                vid = server_url+"/var/" + d
                context = load(vid, loadvar_url)
                temp = KGPLVariable(context["val_id"], context["comment"], vid, context["user"],
                        context["timestamp"])
                refined_dependency.append(temp)
        else:
            refined_dependency.append(d)
    return value(val, comment, user, refined_dependency, verbose)


def value(val, comment, user="anonymous", dependency=[], verbose=False):
    """
    System Internal use only
    """
    if type(val) not in [int, float, tuple, list, dict, str, KGPLValue,
                         KGPLVariable, pandas.DataFrame, ORM.Relation, File,
                         FunctionWithSignature]:
        raise Exception("cannot construct KGPLValue on this type")
    if type(comment) != str:
        raise Exception("Comment needs to be a string.")
    if type(dependency) != list:
        raise Exception("Dependency must be a list of url.")
    if type(user) != str:
        raise Exception("user name must be a string.")
    return KGPLValue(val, comment, user, dependency, verbose=verbose)

# Create a new variable
def variable(var_id, val_id, comment, user="anonymous"):
    """
    Create a KGPLVariable based on the inputs and publish to the server.

    ###### Parameter
    - `val_id`
        vid of the KGPLValue to be stored.
    - `comment`
        A human readable comment (of type `str`) associated with the variable creattion
    - `user`
        User name of the owner of the KGPLVariable, the default value is `anonymous`
    - `dependency`
        A list consisting of the KGPL objects that this KGPLValue depended on. Each element in the list can be one of the three types:
        `KGPLValue`, `KGPLVariable` or `Label`
    - `verbose`: 
        If set to true, more information is produced in the terminal. Otherwise, a succint description is printed when the construction succeeds.

    ###### Return
    A KGPLValue object constructed based on inputs
    """
    if type(val_id) not in [str, KGPLValue]:
        raise Exception("cannot construct KGPLVariable")
    if type(val_id) is KGPLValue:
        val_id = val_id.getVid()
    if type(comment) != str:
        raise Exception("Comment needs to be a string.")
    return KGPLVariable(val_id, comment, var_id, user)


def load_val(vid):
    """
    Fetch the KGPLValue of the corresponding `vid`

    ###### Parameter
    - `vid`
        The vid of the desired KGPLValue 
    
    ###### Return
    A KGPLValue object
    """
    context = load(vid, loadval_url)
    tmp_val = json.loads(context["val"], object_hook=hook)

    if context["pyt"] == 'tuple':
        val = tuple(tmp_val)
    elif context["pyt"] == 'File':
        r = requests.get(os.path.join(
            download_url, str(vid[vid.rfind('/') + 1:])))
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
    """
    Fetch the KGPLValue of the corresponding `vid`

    ###### Parameter
    - `vid`
        The vid of the desired KGPLValue 
    
    ###### Return
    A KGPLValue object
    """
    context = load(vid, loadvar_url)
    return KGPLVariable(context["val_id"], context["comment"], vid, context["user"],
                        context["timestamp"])


# to do: ask if set_var change the owner of the variable?


def set_var(kg_var, val_id, new_comment):
    """
    Update a KGPLVariable and return it.
    ###### Parameters
    - `kg_var`
        KGPLVariable to be updated
    - `val_id`
        ID of the KGPLValue the KGPLVariable should now point to
    - `new_comment`
        Descriptive comment for the value
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
    """
    Fetch the history information of a KGPLVariable object from server

    ###### Parameter
    - `kg_var`: KGPLVariable object whose history information is of interest

    ###### Return
    A list of vids this variable has refered to. The first element is the newest state while the last element is the oldest state.
    """
    r = requests.get(os.path.join(server_url, "gethistory"),
                     json={"vid": kg_var.vid})
    if r.status_code != 200:
        raise Exception("getting history failed")
    l = r.json()["list"]
    return l


def changeNamespace(new_url):
    """ 
    change the namespace of the current program.

    ###### Parameter
    `new_url`
        the new namespace
    """
    global server_url
    print("Old Server: ", server_url)
    new_url = new_url.rstrip('/')
    server_url = new_url
    print("New Server: ", server_url)
    return new_url


def viewNamespace():
    """ 
    print the current namespace
    """
    print("Current Server: ", server_url)
    return server_url

def get_label_content(label):
    """
    Get the content underlying a label

    ###### Parameter
    - `label`
        The label being fetched
    
    ###### Return
    A KGPLVariable object this label represents
    """
    vid = server_url+"/var/"+label
    temp_var = load_var(vid)
    return load_val(temp_var.val_id).val

def publish_new(val, comment, label = None, user="anonymous", dependency=[], verbose=False, label_comment = ""):
    """
    Create a KGPLValue based on the inputs and publish to the server, then __create__ and return a label for this KGPLValue.

    ###### Parameter
    - `val`
        Concrete value to store (We currently support the following types: `int`, `float`, `bool`, `list`, `dict`, `File`, `pandas.DataFrame`, `Relation`)
    - `comment`
        A human readable comment (of type `str`) associated with the value creation
    - `label`
        A human readable name to refer to the new KGPLValue. The default value is `None`. In that case, a default label is generated by the server.
    - `user`
        User name of the owner of this operation, the default value is `anonymous`
    - `dependency`
        A list consisting of the KGPL objects that this KGPLValue depended on. Each element in the list can be one of the three types:
        `KGPLValue`, `KGPLVariable` or `Label`. The default value is empty list.
    - `verbose`: 
        If set to true, more information is produced in the terminal. Otherwise, a succint description is printed when the construction succeeds. The default value is `False`.
    - 'label_comment'
        A human readable comment (of type `str`) associated with the label creation

    ###### Return
    A KGPLVariable object constructed based on inputs
    """
    if label:
        if (label[0:5]=="KNPS_"):
            raise Exception("Customized label name cannot start with KNPS_")
        check_label_occupied(label)
    else:
        label = get_default_label()

    temp = create_value(val, comment, user, dependency, verbose)
    return temp.create_label(label, label_comment)

def publish_update(val, comment, label, user="anonymous", dependency=[], verbose=False, label_comment = ""):
    """
    Create a KGPLValue based on the inputs and publish to the server, then __update__ and return the label for this KGPLValue.

    ###### Parameter
    - `val`
        Concrete value to store (We currently support the following types: `int`, `float`, `bool`, `list`, `dict`, `File`, `pandas.DataFrame`, `Relation`)
    - `comment`
        A human readable comment (of type `str`) associated with the value creation
    - `label`
        The label being updated
    - `user`
        User name of the owner of this operation, the default value is `anonymous`
    - `dependency`
        A list consisting of the KGPL objects that this KGPLValue depended on. Each element in the list can be one of the three types:
        `KGPLValue`, `KGPLVariable` or `Label`. The default value is empty list.
    - `verbose`: 
        If set to true, more information is produced in the terminal. Otherwise, a succint description is printed when the construction succeeds. The default value is `False`.
    - 'label_comment'
        A human readable comment (of type `str`) associated with the label update

    ###### Return
    A KGPLVariable object updated based on inputs
    """
    temp = create_value(val, comment, user, dependency, verbose)
    return temp.update_label(label, label_comment)