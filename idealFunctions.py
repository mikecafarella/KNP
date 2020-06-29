from __future__ import annotations

import KGTypes
import inspect
from query import IR

def get_type_precondition_score(func, *args, **kwargs):
    #
    # TODO: what if # of args != # or params required by the function?
    #
    # print(args)
    # print(kwargs)
    type_annotations = func.__annotations__
    arg_values = {}
    for k, v in zip(type_annotations.keys(), args):
        arg_values[k] = v
    arg_values.update(kwargs)
    # print(arg_values)
    # print(type_annotations)
    scores = []
    for name, arg_value in arg_values.items():
        type_str = type_annotations[name]
        if hasattr(KGTypes, type_str):
            KGtype = getattr(KGTypes, type_str)

            tmp = KGtype(arg_value)

            score = tmp.testIfDataValueIsMemberOfType(arg_value)
            scores.append(score)
        else:
            try:
                type = eval(type_str)
                score = int(isinstance(arg_value, type))
                scores.append(score)
            except:
                print("### Undefined type {}".format(type_str))
    score = sum(scores) / len(scores)
    # if verbose:
    print("Individual param socres:", scores)
    print("Overall score: {}".format(score))
    return score


def check_type_preconditions(func):
    def function_wrapper(*args, **kwargs):
        score = get_type_precondition_score(func, args, kwargs)
        if score < 1:
            raise ValueError("Not a perfect match!")
        print("### Passed type check. Now call {}.".format(func.__name__))
        return func(*args, **kwargs)
    return function_wrapper


# @check_type_preconditions
def PlotTimeSeries(ts1: TimeSeries, ts2: TimeSeries, title: __String__) -> __Image__:
    # return PlotTwoLines(ts1.x, ts1.y, ts1.name, ts2.x, ts2.y, ts2.name, title)
    pass


def PlotTwoLines(x1: __List__, y1: __List__, name1: __String__, x2: __List__, y2: __List__, name2:__String__, title: __String__) -> __Image__:
    # return __InvokeExternal__(kgpsupport.plot, (x1, y1, name1, x2, y2, name2, title))
    pass


# @check_type_preconditions
def CompareGDP(gdp1: nominalGDP, gdp2: nominalGDP) -> __Image__:
    # assert(gdp1.currency == gdp2.currency)
    # assert(gdp1.is-inflation-adjusted == gdp2.is-inflation-adjusted)
    # return PlotTimeSeries(gdp1, gdp2, "GDP")
    pass
    


# @check_type_preconditions
def CompareTimeSeries(ts1: TimeSeries, ts2: TimeSeries, title: __String__) -> __Image__:
    # PythonPlotTwoLines(ts1.getValues(), ts1.getTime(), ts1.getLabel(),
    #                  ts2.getValues(), ts1.getTime(), ts2.getLabel(), title)
    pass



def CompareGDP(region1: PoliticalGeography, region2: PoliticalGeography) -> __Image__:
    # __Assert__(region1.country == region2.country)
    # CompareGDP(region1.gdp, region2.gdp)
    pass

#
# Comparing people
#
def ComparePeople(p1: Person, p2: Person) -> __Table__:
    # return GenerateTable(p1, p2)
    pass

def ComparePoliticians(p1: Politician, p2: Politician) -> __Table__:
    # return GenerateTable(p1, p2, properties=[image, home-state])
    pass

def CompareMovieStars(p1: MovieStar, p2: MovieStar) -> __Table__:
    # return GenerateTable(p1, p2, properties=[image, box-office])
    pass

def GenerateTable(e1: __Entity__, e2: __Entity__, propertyList=[]) -> __Table__:
    # allProperties = e1.__properties__.intersect(e2.__properties__)
    # while len(propertyList) < 3:
    #     propertyList.add(allProperties.pop())
    # return __Table__(propertyList, e1, e2)
    pass


USA_GDP = IR("Q30", KG='wikidata', focus='P2131')
Canada_GDP = IR("Q16", KG='wikidata', focus='P2131')

USA_ts = KGTypes.TimeSeries(USA_GDP)
# Canada_ts = KGTypes.TimeSeries(Canada_GDP)

# Verbose mode
# s1 = get_type_precondition_score(CompareTimeSeries, USA_ts, Canada_ts, "compare ts")
print(USA_ts.attributes)
# print(USA_ts.time)
# print(USA_ts.amount)

# s2 = get_type_precondition_score(CompareTimeSeries, USA_GDP, Canada_GDP, "compare ts")
