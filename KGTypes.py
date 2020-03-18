from abc import ABC, abstractmethod
#
# All following functions assuming using Wikidata Schema
#
from typing import List, Set, Mapping, Tuple
import query
import pandas as pd
import scorer_algorithms
import copy


class Type(ABC):
    def __init__(self, source):
        """ Initiate self.dataframe from the.
            Args:
                source: could be a subclass of Type, or an IR.
            
            Attrs:
                attributes: a dict.
        """
        pass

    @classmethod
    @abstractmethod
    def testIfDataValueIsMemberOfType(cls, source):
        """ Takes as input an IR, 
            returns a float in [0, 1] representing the possbiility of the IR is a memboer of the type.
        """
        pass

    def __getattr__(self, name):
        if self.attributes is None or name not in self.schema:
            return None
        return self.attributes[name]


class __Image__(Type):
    pass


class __List__(Type):
    @classmethod
    def testIfDataValueIsMemberOfType(cls, o):
        if isinstance(o, list):
            return 1
        return 0


class __String__(Type):
    @classmethod
    def testIfDataValueIsMemberOfType(cls, o):
        if isinstance(o, str):
            return 1
        return 0


class TimeSeries(Type):
    entity_id = "Q186588"
    type = "item"
    schema = {
        "time": __List__,
        "amount": __List__
    }

    def testIfDataValueIsMemberOfType(self, _):
        return self.overall_score
    
    def __init__(self, source):
        # if isinstance(source, query.IR):
        #     source = source.properties
        #     # IR = source
        #     # if IR.focus is not None:
        #     #     source = IR[IR.focus]
        #     # else:
        #     #     #
        #     #     # For now, let's assume the user won't pass an entire entity to convert to TimeSeries
        #     #     #
        #     #     raise RuntimeError("Should never do this!")
        # elif isinstance(source, Type):
        #     # TODO: the source might already be TimeSeries
        #     source = source.attributes
        # else:
        #     self.overall_score = 0
        #     return

        self.attributes, self.overall_score = _match(self.schema, source)
        assert(len(self.attributes.keys()) == len(self.schema.keys()))
        
        
        

class MovieStar(Type):
    entity_id = "Q1337738"
    type = "item"
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
    
    def __init__(self, source):
        pass


class Person(Type):
    entity_id = "Q215627"
    type = "item"
    @classmethod
    def testIfDataValueIsMemberOfType(cls, IR):
        if not isinstance(IR, query.IR):
            return 0
        s1 = check_instanceOf_prop(IR, cls.entity_id)
        s2 = check_occupation_prop(IR, cls.entity_id)
        return (s1 + s2) / 2


def _match(schema: Mapping[str, Type], source) -> Mapping:
    rst = {}
    scores = []
    # columns = list(df.columns)
    # if len(columns) < len(schema):
    #     return None, 0
    # for s in schema:
    #     columns.sort(key=lambda col_name: scorer_algorithms._levenshtein_score(col_name, s))
    #     column = columns.pop()
    #     rst[s] = df[column]
    #     scores.append(scorer_algorithms._levenshtein_score(column, s))
    if isinstance(source, query.IR):
        possible_matches = {}
        for pid, df in source.properties.items():
            for column in df.columns:
                possible_matches[pid + "." + str(column)] = df[column]

        print(possible_matches.keys())

        source_labels = list(possible_matches.keys())

        for target_label, _type in schema.items():
            if _type is __List__:
                # source_labels = list(possible_matches.keys())
                source_labels.sort(key=lambda source_label: scorer_algorithms._levenshtein_score(source_label, target_label))
                # tmp = source_labels.pop()
                tmp = source_labels[-1]
                rst[target_label] = possible_matches[tmp]
                scores.append(scorer_algorithms._levenshtein_score(tmp, target_label))
            elif _type is __String__:
                # source_labels = [l.split(".")[1:] for l in list(possible_matches.keys())]
                source_labels.sort(key=lambda source_label: scorer_algorithms._levenshtein_score(source_label, target_label))
                # tmp = source_labels.pop()
                tmp = source_labels[-1]
                rst[target_label] = tmp
                scores.append(scorer_algorithms._levenshtein_score(tmp, target_label))
            else:
                raise ValueError("Not implemented yet")
    elif isinstance(source, Type):
        if source.schema == schema:
            return copy.deepcopy(source.attributes), 1  # TODO: source.overall_score?
        # for label, _type in schema.items():
        #     pass
        raise ValueError("Not implemented yet")
    else:
        raise ValueError("Not implemented yet")
    return rst, sum(scores) / len(scores)



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
