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
                scorers : A list of Scorers
            Return:
                A float number in [0, 1].
        """
        scores = [(s.get_score(self), s.weight) for s in scorers]
        score = overall_aggragator.aggregate(scores)
        self.score = score

        print(str(self)+":              score = {}".format(score))

        return score

    def __str__(self):
        # return "ConcreteMethod: {}\n Refinement: {}\n Mapping: {}\n Query: {}." \
        #     .format(self.c, self.r, self.m, self.q)
        
        return "ConcreteMethod: {}\n Refinement: {}\n Mapping: {}." \
            .format(self.c, self.r, self.m)

    def execute(self):
        pass



