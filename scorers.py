from abc import ABC, abstractmethod
from invocations import Invocation
from typing import List, Set, Mapping, Tuple
import scorer_algorithms
import pandas

_score_types = [
    'Q_R',
    'R_C',
    'R_M',
    'C_M'
]

"""
    Each Scorer return a float in the range [0, 1].
"""

class Scorer(ABC):
    @abstractmethod
    def get_score(self, invocation: Invocation):
        pass


class ScoreAggregator(ABC):
    @abstractmethod
    def aggregate(self, scores: Mapping[str, float]) -> float:
        pass


class AverageAgg(ScoreAggregator):
    def aggregate(self, scores: Mapping[str, float]):
        return sum(scores.values()) / len(scores.values())


class LevenshteinStringSimilarity(Scorer):
    applicable_types = ['Q_R', 'R_C']

    def get_score(self, invocation: Invocation):
        """ Calulate the Levenshtein score between Query.operator_desc and Refinement.description,
                and between Refinement.description and ConcreteMethod.name.
        """
        Q_R = scorer_algorithms._levenshtein_score(invocation.q.operator_desc, invocation.r.description)
        R_C = scorer_algorithms._levenshtein_score(invocation.r.description, invocation.c.name)
        return (Q_R + R_C) / 2


class CosineStringSimilarity(Scorer):
    applicable_types = ['Q_R', 'R_C']

    def get_score(self, invocation: Invocation):
        """ Calulate the Cosine score between Query.operator_desc and Refinement.description,
                and between Refinement.description and ConcreteMethod.name.
        """
        Q_R = scorer_algorithms._cosine_similarity(invocation.q.operator_desc, invocation.r.description)
        R_C = scorer_algorithms._cosine_similarity(invocation.r.description, invocation.c.name)
        return (Q_R + R_C) / 2


class InvolvedEntityAllignment(Scorer):
    """
        Check whether the number of elements in Query.KG_params equal to that of Refinement.involves
    """
    applicable_types = ['Q_R']

    def get_score(self, invocation: Invocation):
        return len(invocation.q.first_params) == len(invocation.r.involves)


class BasicMappingProbability(Scorer):
    """Check whether every selected column in the mapping appeared in Refinement.mapping_desc."""
    applicable_types = ['R_M']

    def get_score(self, invocation: Invocation):
        scores = []
        for variable, value in invocation.m.mapping.items():
            if isinstance(value, str):
                name = value
            elif isinstance(value, pandas.Series):
                name = value.name
            else:
                name = value
            assert(isinstance(name, str))
            name_similarity = max([ max(scorer_algorithms._cosine_similarity(name, p), scorer_algorithms._levenshtein_score(name, p)) \
                for p in invocation.r.mapping_desc])
            scores.append(name_similarity)
        return sum(scores) / len(scores)


class MappingRunnable(Scorer):
    """ Check whether the mapping is runnable on the ConcreteMethod. 
        Because this is kinda like a hard requirement, so if the invocation
        fails the test, -50 is returned. 
    """
    applicable_types = ['C_M']

    def get_score(self, invocation: Invocation):
        try:
            invocation.c.function(invocation.m.mapping)
            return 1
        except:
            return -50