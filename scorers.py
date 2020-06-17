from abc import ABC, abstractmethod
from invocations import Invocation
from typing import List, Set, Mapping, Tuple
import scorer_algorithms
import pandas

_score_types = [
    'Q_R',  # The scorer looks at the Query and Refinement of the Invocation.
    'R_C',  # The scorer looks at the Refinement and ConcreteMethod of the Invocation.
    'R_M',
    'C_M'
]

"""
    Each Scorer return a float in the range [0, 1].
"""

class Scorer(ABC):
    @classmethod
    @abstractmethod
    def get_score(cls, invocation: Invocation):
        pass


class ScoreAggregator(ABC):
    @classmethod
    @abstractmethod
    def aggregate(cls, scores: List):
        """
            Args:
                scores: a list of (score, weight of the scorer) tuples.
        """
        pass


class AverageAgg(ScoreAggregator):
    @classmethod
    def aggregate(cls, scores: List):
        sum_of_scores = sum([t[0] for t in scores])
        sum_of_weights = sum([t[1] for t in scores])
        return sum_of_scores / sum_of_weights


class LevenshteinStringSimilarity(Scorer):
    applicable_types = ['Q_R', 'R_C']
    weight = 1

    @classmethod
    def get_score(cls, invocation: Invocation):
        """ Calulate the Levenshtein score between Query.operator_desc and Refinement.description,
                and between Refinement.description and ConcreteMethod.name.
        """
        Q_R = scorer_algorithms._levenshtein_score(invocation.q.operator_desc, invocation.r.description)
        R_C = scorer_algorithms._levenshtein_score(invocation.r.method_desc, invocation.c.name)
        return cls.weight * (Q_R + R_C) / 2


class CosineStringSimilarity(Scorer):
    applicable_types = ['Q_R', 'R_C']
    weight = 1

    @classmethod
    def get_score(cls, invocation: Invocation):
        """ Calulate the Cosine score between Query.operator_desc and Refinement.description,
                and between Refinement.description and ConcreteMethod.name.
        """
        Q_R = scorer_algorithms._cosine_similarity(invocation.q.operator_desc, invocation.r.description)
        R_C = scorer_algorithms._cosine_similarity(invocation.r.method_desc, invocation.c.name)
        return cls.weight * (Q_R + R_C) / 2


class InvolvedEntityAllignment(Scorer):
    """
        Check whether the number of elements in Query.KG_params equal to that of Refinement.involves
    """
    applicable_types = ['Q_R']
    weight = 1

    @classmethod
    def get_score(cls, invocation: Invocation):
        return cls.weight * len(invocation.q.KG_params) == len(invocation.r.involves)


class BasicMappingProbability(Scorer):
    """Check whether every selected column in the mapping appeared in Refinement.mapping_desc."""
    applicable_types = ['R_M']
    weight = 1

    @classmethod
    def get_score(cls, invocation: Invocation):
        scores = []
        for _, value in invocation.m.mapping.items():
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
        return cls.weight * sum(scores) / len(scores)


class MappingRunnable(Scorer):
    """ Check whether the mapping is runnable on the ConcreteMethod. 
        Because this is kinda like a hard requirement, so if the invocation
        fails the test, -50 is returned. 
    """
    applicable_types = ['C_M']
    weight = 50

    @classmethod
    def get_score(cls, invocation: Invocation):
        try:
            invocation.c.function(**invocation.m.mapping)
            return 1 * cls.weight
        except:
            return 0