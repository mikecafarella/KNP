from abc import ABC, abstractmethod
#
# All following functions assuming using Wikidata Schema
#
import query

class Type(ABC):
    @classmethod
    @abstractmethod
    def testIfDataValueIsMemberOfType(cls, IR):
        """ Takes as input an IR, 
            returns a float in [0, 1] representing the possbiility of the IR is a memboer of the type.
        """
        pass


class __Image__(Type):
    pass


class __String__(Type):
    @classmethod
    def testIfDataValueIsMemberOfType(cls, o):
        if isinstance(o, str):
            return 1
        return 0


class TimeSeries(Type):
    @classmethod
    def testIfDataValueIsMemberOfType(cls, IR):
        return 1


class Politician(Type):
    entity_id = "Q82955"
    type = "item"
    @classmethod
    def testIfDataValueIsMemberOfType(cls, IR):
        if not isinstance(IR, query.IR):
            return 0
        s1 = check_instanceOf_prop(IR, cls.entity_id)
        s2 = check_occupation_prop(IR, cls.entity_id)
        return (s1 + s2) / 2


class nominalGDP(Type):
    entity_id = "P2131"
    type = "property"
    @classmethod
    def testIfDataValueIsMemberOfType(cls, IR):
        if not isinstance(IR, query.IR):
            return 0
        return check_prop(IR, cls.entity_id)


def check_instanceOf_prop(IR, entity_id: str):
    """ Chechk if the entity represented by IR is an instance of the entity with entity_id."""
    PID = 'P31'
    if PID not in IR.properties:
        return 0
    series = IR[PID]["wikidata ID"]
    if entity_id in series:
        return 1
    return 0


def check_occupation_prop(IR, entity_id: str):
    PID = "P106"
    if PID not in IR.properties:
        return 0
    series = IR[PID]["wikidata ID"]
    if entity_id in series:
        return 1
    return 0


def check_prop(IR, prop_id: str):
    if IR.focus == prop_id:
        return 1
    else:
        return 0
    