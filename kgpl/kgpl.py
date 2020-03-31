import uuid
from enum import Enum

ALLVALS = {}
        
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
    def __init__(self, f, lineage=None):
        KGPLValue.__init__(self, f, lineage)

    def __str__(self):
        return str("KGPLFunc " + str(self.id) + ", " + str(self.val))

    def __call__(*args, **kwargs):
        self = args[0]
        f = self.val
        resultval = f(*list(map(lambda x: x.val, args[1:])))
        execval = Execution(self, args[1:])
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

def kgfunc(f, lineage=None):
    return KGPLFuncValue(f, lineage)

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
        

def __kgadd_raw__(x, y):
    return x + y

kgAdd = kgfunc(__kgadd_raw__)


KGPLValue.__add__ = lambda x, y: kgAdd(x, y)




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
    
