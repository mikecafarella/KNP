from query import Query
from typing import List, Set, Mapping, Tuple
from invocations import Invocation
from scorers import *
import methods
import refinements

def generate_parameter_mappings(query: Query, c: methods.ConcreteMethod):
    pass



def generate_candidate_invocations(query: Query):
    candidate_invocations = []
    for r in refinements.available_refinements:
        for c in methods.available_methods:
            c = getattr(methods, c)
            r = getattr(refinements, r)
            mappings = generate_parameter_mappings(query, c)
            for m in mappings:
                candidate_invocations.append(Invocation(c, r, m, query))
    return candidate_invocations


def process_query(query: Query, rank: int=10):
    candidate_invocations = generate_candidate_invocations(query)
    # rst = []
    # cur_min = -100

    scorers = [LevenshteinStringSimilarity, CosineStringSimilarity, InvolvedEntityAllignment, BasicMappingProbability, MappingRunnable]
    aggregator = AverageAgg

    for invocation in candidate_invocations:
        # score = invocation.get_score(scorers, aggregator)
        candidate_invocations.sort(key=lambda invocation: invocation.get_score(scorers, aggregator), reverse=True)
    
    rank = rank if len(candidate_invocations) >= rank else len(candidate_invocations)
    return candidate_invocations[0:rank]