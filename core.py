from query import Query
from typing import List, Set, Mapping, Tuple
from invocations import Invocation
from scorers import *

def generate_candidate_invocations(query: Query) -> List[Invocation]:
    pass


def process_query(query: Query, rank: int=10):
    candidate_invocations = generate_candidate_invocations(query)
    # rst = []
    # cur_min = -100

    scorers = [LevenshteinStringSimilarity, CosineStringSimilarity, InvolvedEntityAllignment, BasicMappingProbability, MappingRunnable]
    aggregator = AverageAgg

    for invocation in candidate_invocations:
        score = invocation.get_score(scorers, aggregator)
