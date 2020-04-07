from __future__ import annotations

import uuid
from enum import Enum

import KGType

ALLVALS = {}
ALLFUNCS = {}
        
class LineageKinds(Enum):
    InitFromInternalOp = 1
    InitFromPythonValue = 2
    InitFromExecution = 3

class Lineage:
    def InitFromInternalOp():
        return Lineage(LineageKinds.InitFromInternalOp, None)

    def InitFromPythonVal():
        return Lineage(LineageKinds.InitFromPythonValue, None)

    def InitFromExecution(srcExecutionId):
        return Lineage(LineageKinds.InitFromExecution, srcExecutionId)

    def __init__(self, lineageKind, prevLineageId):
        self.lineageKind = lineageKind
        self.prevLineageId = prevLineageId

    def __repr__(self):
        return "Lineage kind: " + str(self.lineageKind) + ", prev-lineage-id: " + str(self.prevLineageId)

    def __str__(self):
        return "Lineage kind: " + str(self.lineageKind) + ", prev-lineage-id " + str(self.prevLineageId)

class KGPLValue:
    def __init__(self, val, lineage=None):
        self.val = val        
        if lineage is None:
            self.lineage = Lineage.InitFromPythonVal()
        else:
            self.lineage = lineage

        self.id = uuid.uuid4()
        self.url = "<unregistered>"
        self.annotations = []
        ALLVALS[self.id] = self

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return "concretevalue: " + str(self.val) + "\nid: " + str(self.id) + "\nlineage: " + str(self.lineage) + "\nurl: " + str(self.url) + "\nannotations: " + str(self.annotations)

    def showLineageTree(self, depth=0):
        print(" " * depth + str(self))
        print(" " * depth + str(self.lineage.lineageKind))
        print()
        if self.lineage.prevLineageId is not None:
            ALLVALS[self.lineage.prevLineageId].showLineageTree(depth=depth+2)


class KGPLInt(KGPLValue):
    def __init__(self, x, lineage=None):
        super().__init__(int(x), lineage)

    def __str__(self):
        return str("KGPLInt " + str(self.id) + ", " + str(self.val))

class KGPLStr(KGPLValue):
    def __init__(self, x, lineage=None):
        KGPLValue.__init__(self, str(x), lineage)

    def __str__(self):
        return str("KGPLStr " + str(self.id) + ", " + str(self.val))


class KGPLFloat(KGPLValue):
    def __init__(self, x, lineage=None):
        KGPLValue.__init__(self, float(x), lineage)

    def __str__(self):
        return str("KGPLFloat " + str(self.id) + ", " + str(self.val))


class KGPLFuncValue(KGPLValue):
    def __init__(self, f, name, lineage=None):
        super().__init__(f, lineage)
        self.name = f.__name__ if name is None else name
        ALLFUNCS.setdefault(self.name, []).append(self)  # could be: self.id

    def __str__(self):
        return str("KGPLFunc " + str(self.id) + ", " + str(self.val))

    def __call__(self, *args, **kwargs):
        f = self.val
        resultval = f(*list(map(lambda x: x.val, args)))
        execval = Execution(self, args)
        return kgval(resultval, lineage=Lineage.InitFromExecution(execval.id))


def kgint(x, lineage=None):
    return KGPLInt(x, lineage)

def kgstr(x, lineage=None):
    return KGPLValue(x, lineage)

def kgfloat(x, lineage=None):
    return KGPLFloat(x, lineage)

def kgval(x, lineage=None):
    if isinstance(x, int):
        return kgint(x, lineage)
    elif isinstance(x, str):
        return kgstr(x, lineage)
    elif isinstance(x, float):
        return kgfloat(x, lineage)
    else:
        raise Exception("Cannot create KG value for", x)

def kgfunc(f, name=None, lineage=None):
    return KGPLFuncValue(f, name, lineage)

class Execution(KGPLValue):
    def __init__(self, funcValue, inputs):
        super().__init__((funcValue, inputs), lineage=Lineage.InitFromInternalOp())

    def __repr__(self):
        funcVal = self.val[0]
        inputs = self.val[1]
        return "Execution funcValue: " + str(funcVal) + " inputs: " + str(inputs)

    def __str__(self):
        return str("__Execution__ " + str(self.id))

    def showLineageTree(self, depth=0):
        funcVal, inputs = self.val
        print(" " * depth + str(self))
        print(" " * depth + str(self.lineage.lineageKind))
        print()
        ALLVALS[funcVal.id].showLineageTree(depth=depth+2)
        for x in inputs:
            ALLVALS[x.id].showLineageTree(depth=depth+2)
        

def __kgadd_raw__(x: Integer, y: Integer):
    return x + y

kgAdd = kgfunc(__kgadd_raw__)


KGPLValue.__add__ = lambda x, y: kgAdd(x, y)



def __kgadd_raw__(x: String, y: String):
    return "str 1: {} + str 2: {}".format(x, y)
kgfunc(__kgadd_raw__)


class KGPLVariable:
    def __init__(self, val: KGPLValue):
        self.id = uuid.uuid4()
        self.currentvalue = val
        self.owner = "michjc"
        self.url = "<unregistered>"
        self.annotations = []

    def reassign(self, val: KGPLValue):
        self.currentvalue = val

    def __str__(self):
        return str(self.currentvalue)

    def __repr__(self):
        return "id: " + str(self.id) + "\nowner: " + str(self.owner) + "\nurl: " + str(self.url) + "\nannotations: " + str(self.annotations) + "\ncurrentvalue: " + str(self.currentvalue)


def kgplSquare(x):
    return KGPLValue(x * x)


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


def get_type_precondition_score(kgpl_func: KGPLFuncValue, *args, **kwargs):
    #
    # TODO: what if # of args != # or params required by the function?
    #
    func = kgpl_func.val
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
            score = KGtype.typefuc(arg_value)
            scores.append(score)
        else:
            raise ValueError("### Undefined type {}".format(type_str))
    score = sum(scores) / len(scores)
    # print("Individual param socres:", scores)
    # print("Overall score: {}".format(score))
    return score
