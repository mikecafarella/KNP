from __future__ import annotations

# ----------


from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, \
    PickleType, Float, Table, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, make_transient

engine = create_engine('sqlite:///KGPLData.db', echo=False)
Base = declarative_base(bind=engine)
# ----------
association_table = Table('association', Base.metadata,
                          Column('left_id', Integer,
                                 ForeignKey('KGPLValue.id')),
                          Column('right_id', Integer,
                                 ForeignKey('KGPLVariable.currentvalue'))
                          )

import uuid
import time
import pickle
from enum import Enum

from .KNPSStore import KNPSStore

import KGType
from query import IR
import jsonpickle

ALLVALS = {}
ALLFUNCS = {}
# store = KNPSStore('http://lasagna.eecs.umich.edu:8080')
store = KNPSStore(None)

wikiMap = {}


def getValue(id):
    return store.GetValue(id)


def getVariable(varName):
    return store.GetVariable(varName)


def Wiki_Dict_Transformer(entity_id):
    IR_temp = IR(entity_id, 'wikidata')
    result = {}
    result["entity_id"] = entity_id
    result["description"] = IR_temp.desc
    result["name"] = IR_temp.label
    result["property"] = IR_temp.properties
    result["modified"] = IR_temp.modified
    return result


class LineageKinds(Enum):
    InitFromInternalOp = 1
    InitFromPythonValue = 2
    InitFromExecution = 3
    InitFromKG = 4


class Lineage:
    @staticmethod
    def InitFromInternalOp():
        return Lineage(LineageKinds.InitFromInternalOp, None)

    @staticmethod
    def InitFromPythonVal():
        return Lineage(LineageKinds.InitFromPythonValue, None)

    @staticmethod
    def InitFromExecution(srcExecutionId):
        return Lineage(LineageKinds.InitFromExecution, srcExecutionId)

    def __init__(self, lineageKind, prevLineageId):
        self.lineageKind = lineageKind
        self.prevLineageId = prevLineageId

    def __repr__(self):
        return "Lineage kind: " + str(
            self.lineageKind) + ", prev-lineage-id: " + str(self.prevLineageId)

    def __str__(self):
        return "Lineage kind: " + str(
            self.lineageKind) + ", prev-lineage-id " + str(self.prevLineageId)


class KGPLValue(Base):
    __tablename__ = 'KGPLValue'
    id = Column(UnicodeText, primary_key=True)
    val = Column(PickleType)
    lineage = Column(PickleType, nullable=True)
    url = Column(UnicodeText)
    annotations = Column(UnicodeText)
    discriminator = Column(String(20))
    children = relationship("KGPLVariable", secondary=association_table)

    __mapper_args__ = {
        'polymorphic_on': discriminator,
        'polymorphic_identity': 'KGPLValue'
    }

    @staticmethod
    def LoadFromURL(url):
        if url.startswith("localhost"):
            with open("." + url, 'rb') as f:
                return pickle.load(f)
        #
        # TODO: KGPL Sharing Service
        #

    def __init__(self, val, lineage=None):
        self.val = val
        if lineage is None:
            self.lineage = Lineage.InitFromPythonVal()
        else:
            self.lineage = lineage

        self.id = str(uuid.uuid4())
        self.url = "<unregistered>"
        self.annotations = "[]"
        ALLVALS[self.id] = self

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return "concretevalue: " + str(self.val) + "\nid: " + str(
            self.id) + "\nlineage: " + str(self.lineage) + "\nurl: " + str(
            self.url) + "\nannotations: " + str(self.annotations)
        # return "concretevalue: " + str(self.val) + "\nid: " + str(
        #     self.id) + "\nnurl: " + str(
        #     self.url) + "\nannotations: " + str(self.annotations)

    def register(self, server="central_server"):
        self.url = server + "/{}".format(self.id)
        if server == "localhost":
            store.StoreValues([self])
        else:
            store.StoreValues([self])
            store.PushValues()
        return self.url

    def showUrl(self):
        print(self.url)

    def showLineageTree(self, depth=0):
        print(" " * depth + str(self))
        print(" " * depth + str(self.lineage.lineageKind))
        print()
        if self.lineage.prevLineageId is not None:
            ALLVALS[self.lineage.prevLineageId].showLineageTree(
                depth=depth + 2)


class KGPLInt(KGPLValue):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLInt'
    }

    # love = Column(Integer, nullable=True)

    def __init__(self, x, lineage=None):
        # self.love = 42

        super().__init__(int(x), lineage)

    def __str__(self):
        return str("KGPLInt " + str(self.id) + ", " + str(self.val))


class KGPLStr(KGPLValue):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLStr'
    }

    def __init__(self, x, lineage=None):
        KGPLValue.__init__(self, str(x), lineage)

    def __str__(self):
        return str("KGPLStr " + str(self.id) + ", " + str(self.val))


class KGPLFloat(KGPLValue):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLFloat'
    }

    def __init__(self, x, lineage=None):
        KGPLValue.__init__(self, float(x), lineage)

    def __str__(self):
        return str("KGPLFloat " + str(self.id) + ", " + str(self.val))


class KGPLList(KGPLValue, list):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLList'
    }

    def __init__(self, x, lineage=None):
        x = [item if isinstance(item, KGPLValue) else kgval(item) for item in
             x]
        KGPLValue.__init__(self, x, lineage)

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


class KGPLTuple(KGPLValue, Base):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLTuple'
    }

    def __init__(self, x, lineage=None):
        temp = ()
        for item in x:
            if isinstance(item, KGPLValue):
                temp += (item,)
            else:
                temp += (kgval(item),)
        x = temp
        KGPLValue.__init__(self, x, lineage)

    def __str__(self):
        return str("KGPLTuple " + str(self.id) + ",\n" + str(self.val))

    def __len__(self):
        return len(self.val)

    def __getitem__(self, key):
        # TODO: lineage
        return self.val[key]

    def __iter__(self):
        for e in self.val:
            yield e

    def isTuple(self):
        pass


class KGPLDict(KGPLValue, dict, Base):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLDict'
    }

    def __init__(self, x, lineage=None):
        temp = {}
        for key, value in x.items():
            if isinstance(value, KGPLValue):
                temp[key] = value
            else:
                temp[key] = kgval(value)
        x = temp
        KGPLValue.__init__(self, x, lineage)

    def __str__(self):
        strings = []
        strings.append("KGPLDictionary " + str(self.id))
        for key, value in self.val.items():
            strings.append("--------------------")
            strings.append("Key: " + str(key))
            strings.append("Value: " + str(value))
            strings.append("--------------------")
        return '\n'.join(strings)

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

    def isDictionary(self):
        pass


'''
class KGPLWiki(KGPLValue, Base):
    __tablename__ = 'KGPLWiki'
    id = Column(UnicodeText, primary_key=True)
    val = Column(Unicode)  # format is Q100000
    lineage = Column(PickleType, nullable=True)
    url = Column(UnicodeText)
    annotations = Column(UnicodeText, nullable=True)
    IR = Column(PickleType, nullable=True)
    entity_id = Column(Unicode)
    description = Column(Unicode, nullable=True)
    name = Column(Unicode, nullable=True)
    properties = Column(PickleType, nullable=True)
    def __init__(self, x, lineage=None):
        KGPLValue.__init__(self, x, lineage)
        self.IR = IR(x, 'wikidata')
        self.entity_id = x
        self.description = self.IR.desc
        self.name = self.IR.label
        self.properties = self.IR.properties
    def __str__(self):
        return str(
            "KGPLWikiData " + str(self.id) + ",\n Name: " + str(self.name) +
            ",\n Entity_id: " + str(
                self.entity_id) + ",\n Description: " + self.description)
'''


class KGPLFuncValue(KGPLValue):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLFuncValue'
    }
    KGPLFuncValue_name = Column(PickleType, nullable=True)

    def __init__(self, f, name, lineage=None):
        super().__init__(f, lineage)
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
        execval = Execution(self, args, kwargs)

        if not isinstance(resultval, KGPLValue):
            return kgval(resultval,
                         lineage=Lineage.InitFromExecution(execval.id))
        else:
            resultval.lineage = Lineage.InitFromExecution(execval.id)
            return resultval


class KGPLEntityValue(KGPLValue):
    __mapper_args__ = {
        'polymorphic_identity': 'KGPLEntityValue'
    }

    def __init__(self, text_reference, kg="wikidata", lineage=None):
        """text_reference (str): KG references like Q30."""
        if kg.lower() != "wikidata":
            raise RuntimeError("Unimplemented kg {}".format(kg))

        if kg.lower() == "wikidata":
            entiy_id = text_reference.split(".")[0]
            # print(entiy_id)
            property_id = text_reference.split(".")[
                1] if "." in text_reference else None
            # print(property_id)
            super().__init__(IR(entiy_id, "wikidata", focus=property_id),
                             lineage)

    def __str__(self):
        return str("KGPLEntityValue " + str(self.id) + ", " + str(self.val))


def kgint(x, lineage=None):
    return KGPLInt(x, lineage)


def kgstr(x, lineage=None):
    return KGPLStr(x, lineage)


def kgfloat(x, lineage=None):
    return KGPLFloat(x, lineage)


def kgplSquare(x):
    return KGPLValue(x * x)


def kgval(x, lineage=None):
    if isinstance(x, KGPLValue):
        return x

    if x is None:
        return kgstr("None")
    elif isinstance(x, int):
        return kgint(x, lineage)
    elif isinstance(x, str):
        return kgstr(x, lineage)
    elif isinstance(x, float):
        return kgfloat(x, lineage)
    elif isinstance(x, dict):
        return KGPLDict(x, lineage)
    elif hasattr(x, "isTuple"):
        return KGPLTuple(x, lineage)
    elif hasattr(x, "__iter__"):
        return KGPLList(x, lineage)
    #
    # other values? KGPLEntity
    #
    else:
        raise Exception("Cannot create KG value for", x)


def kgfunc(f, name=None, lineage=None):
    return KGPLFuncValue(f, name, lineage)


class Execution(KGPLValue):
    def __init__(self, funcValue, args, kwargs):
        super().__init__((funcValue, args, kwargs),
                         lineage=Lineage.InitFromInternalOp())

    def __repr__(self):
        funcVal = self.val[0]
        inputs = self.val[1:]
        return "Execution funcValue: " + str(funcVal) + " inputs: " + str(
            inputs)

    def __str__(self):
        return str("__Execution__ " + str(self.id))

    def showLineageTree(self, depth=0):
        funcVal = self.val[0]
        inputs = self.val[1:]
        print(" " * depth + str(self))
        # print(" " * depth + str(self.lineage.lineageKind))
        print()
        ALLVALS[funcVal.id].showLineageTree(depth=depth + 2)
        for x in inputs:
            ALLVALS[x.id].showLineageTree(depth=depth + 2)


# def __kgadd_raw__(x: Integer, y: Integer):
#     return x + y

# kgAdd = kgfunc(__kgadd_raw__)

# KGPLValue.__add__ = lambda x, y: kgAdd(x, y)


class KGPLVariable(Base):
    __tablename__ = 'KGPLVariable'
    id = Column(UnicodeText, primary_key=True)
    timestamp = Column(Float, primary_key=True)
    currentvalue = Column(UnicodeText, nullable=True)  # TODO: Foreign key
    owner = Column(UnicodeText, nullable=True)
    url = Column(UnicodeText, nullable=True)
    annotations = Column(UnicodeText, nullable=True)
    # TODO: Currently we have redundant field "history val" in the database
    # historical_vals = Column(PickleType, nullable=True)
    discriminator = Column(String(20))
    # wikimap = relationship("Wikimap", uselist=False, back_populates="KGPLVariable")

    __mapper_args__ = {
        'polymorphic_on': discriminator,
        'polymorphic_identity': 'KGPLVariable'
    }

    @staticmethod
    def LoadFromURL(url):
        if url.startswith("localhost"):
            with open("." + url, 'rb') as f:
                return pickle.load(f)
        #
        # TODO: KGPL Sharing Service
        #

    def __init__(self, val: KGPLValue):
        self.id = None  # after registration, it will have an id.
        self.currentvalue = val.id  # uuid of KGPLValue
        self.owner = "minions"  # TODO: automatically assign owner
        self.url = "<unregistered>"
        self.annotations = "[]"
        self.timestamp = time.time()
        self.historical_vals = [(time.time(), val.id)]
        store.StoreValues([val, ])  # store the KGPLValue to local database

    def __str__(self):
        return "uuid for the current related KGPLValue: " + self.currentvalue

    def __repr__(self):
        return "id: " + str(self.id) + "\nowner: " + str(
            self.owner) + "\nurl: " + str(self.url) + "\nannotations: " + str(
            self.annotations) + "\ncurrentvalue: " + str(self.currentvalue)

    def registerVariable(self):
        """
        self.varName = store.RegisterVariable(
            self.currentvalue, self.historical_vals[0][0])
        if isinstance(self.currentvalue, KGPLWiki):
            wikiMap[self.currentvalue.entity_id] = self.varName
        """

        """
        Session = scoped_session(sessionmaker(bind=engine))
        s = Session()
        fetch = s.query(KGPLValue).filter(
            KGPLValue.id == self.currentvalue).one_or_none()
        if not fetch:
            print("value not found in db but should be found")
        fetch.register()
        """

        # TODO: make sure the related value is registered as well
        """
        Register variable: push to a centralized remote database on the
        parent server. (According to decision on May 20th)
        """
        # self.url = "registered"
        store.RegisterVariable(self)

    # def initOrUpdate(self, varName):
    #     if 'var/' in varName:
    #         if varName[0:3] == 'var':
    #             self = getVariable(varName[4:])
    #     else:
    #         self = getVariable(varName)
    #     if not self:
    #         self.registerVariable()
    #     return self

    def reassign(self, val: KGPLValue):
        make_transient(self)

        self.currentvalue = val.id
        print("---------",self.timestamp)

        self.timestamp = time.time()
        print("---------",self.timestamp)

        self.historical_vals.append((self.timestamp, val.id))
        store.StoreValues([val, ])
        store.SetVariable(self)

    def viewHistory(self):
        i = 0
        print("History of " + str(self.id))
        for pair in self.historical_vals:
            print("Modification " + str(i))
            print("Timestamp: " + str(pair[0]))
            print("Value_id: " + str(pair[1]))
            i = i + 1
            print()


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
    if func.__defaults__ is not None:  # in case there are no kwargs
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


Base.metadata.create_all()
