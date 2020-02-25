from methods import ConcreteMethod
from query import Query
from typing import List, Set, Mapping, Tuple

class Invocation:
    def __init__(self, c: ConcreteMethod, r, m, q: Query):
        """ Instantiate an Invocation. """
        self.c = c
        self.r = r
        self.m = m
        self.q = q

    def get_overall_probability(self, scorers: List, overall_aggragator):
        """ Get an overall score of the Invocation. 
            Args:
                scorers: {type such as 'Q_R': [Scorer 1, Scorer 2]}
            Return:
                A float number in [0, 1].
        """
        scores = [s.get_score(self) for s in scorers]
        score = overall_aggragator.aggregate(scores)
        self.score = score
        return score 

    def execute(self):
        pass



