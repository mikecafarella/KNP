from query import Query
from typing import List, Set, Mapping, Tuple
from invocations import Invocation
from scorers import *
import methods
import refinements
import inspect
import itertools
import mappings

def generate_parameter_mappings(query: Query, c: methods.ConcreteMethod):
    """
        Args:
            query: a Query instance.
            c: a ConcreteMethod instance.
        Returns:
            a list of Mapping instances.
    """
    variables = list(inspect.signature(c.function).parameters.keys())
    possible_values = []  # all the possible values that could be passed into the ConcreteMethod
    for KG_param, IR in query.KG_params.items():
        for property_id, df in IR.properties.items():
            for column in df.columns:
                string = KG_param + "." + property_id + "." + column if IR.focus is None else KG_param + "." + column
                possible_values.append(string)
                possible_values.append(df[column].rename(string))
    possible_values += query.pos_args
    #
    # TODO: add query.keyword_args into possible values?
    #  
    print(len(possible_values))
    print(len(variables))
    # assert(0)
    for mapping in itertools.product(possible_values, repeat=len(variables)):
        yield mappings.Mapping(mapping, variables)


def generate_candidate_invocations(query: Query, limit=None):
    print("Begin to generate candidate Invocations.")
    candidate_invocations = []
    for c in methods.available_methods:
        c = getattr(methods, c)()
        for m in generate_parameter_mappings(query, c):
            for r in refinements.available_refinements:
                r = getattr(refinements, r)
                candidate_invocations.append(Invocation(c, r, m, query))
                print("Generated {}th Invocation.".format(len(candidate_invocations)))
                # print(str(candidate_invocations[-1]))
                if limit and len(candidate_invocations) == limit:
                    return candidate_invocations
    return candidate_invocations


def process_query(query: Query, rank: int=10, limit=None):
    """
        limit: the maximun number of candidate invocations generated.
    """
    candidate_invocations = generate_candidate_invocations(query, limit)

    scorers = [LevenshteinStringSimilarity, CosineStringSimilarity, InvolvedEntityAllignment, BasicMappingProbability, MappingRunnable]
    aggregator = AverageAgg
    print("Begin to calculate scores of Invocations.")
    print()
    print()
    print()
    candidate_invocations.sort(key=lambda invocation: invocation.get_overall_probability(scorers, aggregator), reverse=True)
    
    rank = rank if len(candidate_invocations) >= rank else len(candidate_invocations)
    return candidate_invocations[0:rank]