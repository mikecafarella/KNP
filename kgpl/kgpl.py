from __future__ import annotations
from dataclasses import dataclass

import uuid
import os
import pickle
from enum import Enum
import datetime

import KGType
from query import IR

ALLVALS = {}
ALLFUNCS = {}
        
class LineageKinds(Enum):
    InitFromInternalOp = 1
    InitFromPythonValue = 2
    InitFromExecution = 3
    InitFromKG = 4
    ExecutionInputs = 5
    Arguments = 6
    Code = 7

class Lineage:
    """
        Attrs:
            lineageKind,
            KGPLValueID
    """
    @staticmethod
    def InitFromInternalOp():
        return Lineage(LineageKinds.InitFromInternalOp, None)

    @staticmethod
    def InitFromPythonVal():
        return Lineage(LineageKinds.InitFromPythonValue, None)

    @staticmethod
    def InitFromExecution(srcExecutionId):
        return Lineage(LineageKinds.InitFromExecution, srcExecutionId)
    
    @staticmethod
    def InitFromKG():
        #
        # TODO: do we wanna track which KG and ID here?
        #
        return Lineage(LineageKinds.InitFromKG, None)

    def __init__(self, lineageKind, KGPLValueID):
        self.lineageKind = lineageKind
        self.KGPLValueID = KGPLValueID

    def __repr__(self):
        return "Lineage kind: " + str(self.lineageKind) + ", KGPL ID:" + str(self.KGPLValueID) + "."

    def __str__(self):
        return "Lineage kind: " + str(self.lineageKind) + ", KGPL ID:" + str(self.KGPLValueID) + "."


class KGPLValue:
    """
        Attrs:
            val.
            lineages: a list of Lineage instances.
    """
    @staticmethod
    def LoadFromURL(url):
        if url.startswith("localhost"):
            with open("."+url, 'rb') as f:
                return pickle.load(f)
        #
        # TODO: KGPL Sharing Service
        #

    def __init__(self, val, lineages=None):
        self.val = val
        self.lineages = lineages if lineages is not None else [Lineage.InitFromPythonVal()]
        self.id = uuid.uuid4()
        self.url = "<unregistered>"
        self.annotations = []
        ALLVALS[self.id] = self

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return "concretevalue: " + str(self.val) + "\nid: " + str(self.id) + "\nlineages: " + ", ".join(self.lineages) + "\nurl: " + str(self.url) + "\nannotations: " + str(self.annotations)

    def register(self, server):
        self.url = server + "/{}".format(self.id)
        if server == "localhost":
            if not os.path.exists(".localhost"):
                os.mkdir(".localhost")
            file_name = '.localhost/{}'.format(self.id)
            with open(file_name, 'wb') as f:
                pickle.dump(self, f)
            # assume: any lineages are shared automatically
            for lineage in self.lineages:
                if lineage.KGPLValueID is None:
                    continue
                ALLVALS[lineage.KGPLValueID].register(server)
            return self.url


    def showLineageTree(self, depth=0):
        print(" " * depth + str(self))
        # print(" " * depth + str(self.lineage.lineageKind))
        print()
        for lineage in self.lineages:
            if lineage.KGPLValueID is not None:
                print(" " * (depth + 2) + str(lineage.lineageKind))
                ALLVALS[lineage.KGPLValueID].showLineageTree(depth=depth+2)


class KGPLInt(KGPLValue):
    def __init__(self, x, lineages=None):
        super().__init__(int(x), lineages)

    def __str__(self):
        return str("KGPLInt " + str(self.id) + ", " + str(self.val))


class KGPLStr(KGPLValue):
    def __init__(self, x, lineages=None):
        KGPLValue.__init__(self, str(x), lineages)

    def __str__(self):
        return str("KGPLStr " + str(self.id) + ", " + str(self.val))


class KGPLFloat(KGPLValue):
    def __init__(self, x, lineages=None):
        KGPLValue.__init__(self, float(x), lineages)

    def __str__(self):
        return str("KGPLFloat " + str(self.id) + ", " + str(self.val))


class KGPLList(KGPLValue, list):
    def __init__(self, x, lineages=None):
        x = [item if isinstance(item, KGPLValue) else kgval(item, lineages) for item in x]
        KGPLValue.__init__(self, x, lineages)

    def __str__(self):
        return str("KGPLList " + str(self.id) + ",\n" + str(self.val))

    def __len__(self):
        return len(self.val)

    def __getitem__(self, key):
        # TODO: lineage
        return self.val[key]
    
    def __setitem__(self, key, value):
        # TODO: lineage
        self.val[key] = kgval(value)

    def __iter__(self):
        for e in self.val:
            yield e   


class KGPLDict(KGPLValue, dict):
    pass


class KGPLFuncValue(KGPLValue):
    def __init__(self, f, name, lineages=None):
        super().__init__(f, lineages)
        self.name = f.__name__ if name is None else name
        ALLFUNCS.setdefault(self.name, []).append(self)  # could be: self.id

    def __str__(self):
        return str("KGPLFunc " + str(self.id) + ", " + str(self.val))

    def __call__(self, *args, **kwargs):
        """
            All args, and kwargs should be of type KGPLValue.
        """
        f = self.val
        resultval = f(*list(map(lambda x: x.val, args)))
        #
        # Todo: what about kwargs?
        #
        execval = Execution(self, args, kwargs, resultval)

        if not isinstance(resultval, KGPLValue):
            return kgval(resultval, lineages=[Lineage.InitFromExecution(execval.id)])
        else:
            resultval.lineages = [Lineage.InitFromExecution(execval.id)]
            return resultval


class KGPLEntityValue(KGPLValue):
    def __init__(self, text_reference, kg="wikidata", lineages=None):
        """text_reference (str): KG references like Q30."""
        lineages = lineages if lineages is not None else [Lineage.InitFromKG()]
        if kg.lower() != "wikidata":
            raise RuntimeError("Unimplemented kg {}".format(kg))

        if kg.lower() == "wikidata":
            entiy_id = text_reference.split(".")[0]
            property_id = text_reference.split(".")[1] if "." in text_reference else None
            super().__init__(IR(entiy_id, "wikidata", focus=property_id), lineages)

    def __str__(self):
        return str("KGPLEntityValue " + str(self.id) + ", " + str(self.val))


def kgint(x, lineages=None):
    return KGPLInt(x, lineages)

def kgstr(x, lineages=None):
    return KGPLStr(x, lineages)

def kgfloat(x, lineages=None):
    return KGPLFloat(x, lineages)

def kgplSquare(x):
    return KGPLValue(x * x)

def kgval(x, lineages=None):
    if isinstance(x, KGPLValue):
        return x
    
    if isinstance(x, int):
        return kgint(x, lineages)
    elif isinstance(x, str):
        return kgstr(x, lineages)
    elif isinstance(x, float):
        return kgfloat(x, lineages)
    elif hasattr(x, "__iter__"):
        return KGPLList(x, lineages)
    #
    # other values? KGPLEntity
    #
    else:
        raise Exception("Cannot create KG value for", x)


def kgfunc(f, name=None, lineages=None):
    return KGPLFuncValue(f, name, lineages)

@dataclass
class ExecutionDetails:
    time: datetime.datetime
    user: str
    Python_version: str

class Execution(KGPLValue):
    def __init__(self, funcValue, args, kwargs, resultval):
        # super().__init__((funcValue, args, kwargs), lineage=Lineage.InitFromInternalOp())
        lineages = [Lineage(LineageKinds.Code, funcValue.id)]
        lineages += [Lineage(LineageKinds.Arguments, arg.id) for arg in args]
        for kward, value in kwargs.items():
            lineages.append(Lineage(LineageKinds.Arguments, value.id))
        #
        # TODO: lineage (executionInputs) unimplemented!
        #

        #
        # TODO: user??? 
        #
        val = ExecutionDetails(datetime.datetime.now(), "yuze", "3.8.1")
        super().__init__(val, lineages=lineages)


    def __repr__(self):
        return "Execution details: \n" + str(self.val)

    def __str__(self):
        return str("Execution " + str(self.id))

    # def showLineageTree(self, depth=0):
    #     funcVal = self.val[0]
    #     inputs = self.val[1:]
    #     print(" " * depth + str(self))
    #     print(" " * depth + str(self.lineage.lineageKind))
    #     print()
    #     ALLVALS[funcVal.id].showLineageTree(depth=depth+2)
    #     for x in inputs:
    #         ALLVALS[x.id].showLineageTree(depth=depth+2)

# def __kgadd_raw__(x: Integer, y: Integer):
#     return x + y

# kgAdd = kgfunc(__kgadd_raw__)

# KGPLValue.__add__ = lambda x, y: kgAdd(x, y)



class KGPLVariable:
    @staticmethod
    def LoadFromURL(url):
        if url.startswith("localhost"):
            with open("."+url, 'rb') as f:
                return pickle.load(f)
        #
        # TODO: KGPL Sharing Service
        #

    def __init__(self, val: KGPLValue):
        self.id = uuid.uuid4()
        self.currentvalue = val
        self.owner = "michjc"
        self.url = "<unregistered>"
        self.annotations = []
        self.historical_vals = [val]

    def reassign(self, val: KGPLValue):
        self.historical_vals.append(self.currentvalue)
        self.currentvalue = val
        

    def __str__(self):
        return str(self.currentvalue)

    def __repr__(self):
        return "id: " + str(self.id) + "\nowner: " + str(self.owner) + "\nurl: " + str(self.url) + "\nannotations: " + str(self.annotations) + "\ncurrentvalue: " + str(self.currentvalue)

    def register(self, server):
        self.url = server + "/{}".format(self.id)
        if server == "localhost":
            if not os.path.exists(".localhost"):
                os.mkdir(".localhost")
            file_name = '.localhost/{}'.format(self.id)
            with open(file_name, 'wb') as f:
                pickle.dump(self, f)
            # assume: any lineages are shared automatically
            for lineage in self.lineages:
                if lineage.KGPLValueID is None:
                    continue
                ALLVALS[lineage.KGPLValueID].register(server)
            return self.url
        


###################################################
def call_func_by_name(func_name, *args, **kwargs):
    if func_name not in ALLFUNCS:
        raise ValueError("Function {} not found".format(func_name))
    func_list = ALLFUNCS[func_name]
    cur_func = None
    cur_score = 0
    scores = {}
    for kgpl_func in func_list:
        score = get_type_precondition_score(kgpl_func, *args, **kwargs)
        scores[kgpl_func.id] = score
        if score > cur_score:
            cur_score = score
            cur_func = kgpl_func
    # print(scores)
    return cur_func(*args, **kwargs)


def call_func_by_id(id, *args, **kwargs):
    if id not in ALLVALS:
        raise ValueError("Function {} not found".format(id))
    return ALLVALS[id](*args, **kwargs)


def get_type_precondition_score(kgpl_func: KGPLFuncValue, *args, **kwargs):
    func = kgpl_func.val
    #
    # what if # of args != # or params required by the function? return 0
    #
    all_args_count = func.__code__.co_argcount
    if func.__defaults__ is not None:  #  in case there are no kwargs
        kwargs_count = len(func.__defaults__)
    else:
        kwargs_count = 0
    positinal_args_count = all_args_count - kwargs_count

    if len(args) != positinal_args_count:
        return 0
    
    if len(kwargs) > kwargs_count:
        return 0

    type_annotations = func.__annotations__
    arg_values = {}
    for k, v in zip(type_annotations.keys(), args):
        arg_values[k] = v
    arg_values.update(kwargs)
    
    scores = []
    for name, arg_value in arg_values.items():
        type_str = type_annotations[name]
        if hasattr(KGType, type_str):
            KGtype = getattr(KGType, type_str)
            score = KGtype.typefunc(arg_value)
            scores.append(score)
        else:
            raise ValueError("### Undefined type {}".format(type_str))
    score = sum(scores) / len(scores)
    # print("Individual param socres:", scores)
    # print("Overall score: {}".format(score))
    return score
