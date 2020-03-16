from __future__ import annotations

import KGTypes
from KGTypes import TimeSeries, __Image__, nominalGDP, __String__
import inspect
from query import IR


def check_type_preconditions(func):
    def function_wrapper(*args, **kwargs):
        args = locals().get('args')
        kwargs = locals().get('kwargs')
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
                score = KGtype.testIfDataValueIsMemberOfType(arg_value)
                scores.append(score)
            else:
                try:
                    type = eval(type_str)
                    score = int(isinstance(arg_value, type))
                    scores.append(score)
                except:
                    print("### Undefined type {}".format(type_str))
        score = sum(scores) / len(scores)
        print(scores)
        if score < 1:
            raise ValueError("Not a perfect match!")
        print("### Passed type check. Now call {}.".format(func.__name__))
        return func(*args, **kwargs)
    return function_wrapper


@check_type_preconditions
def PlotTimeSeries(ts: TimeSeries, title: __String__) -> __Image__:
    # return PythonPlotOneLine(ts.getValues(), ts.getTime(), ts.getLabel(), title)
    pass


@check_type_preconditions
def CompareGDP(gdp1: nominalGDP, gdp2: nominalGDP) -> __Image__:
    # __Assert__(gdp1.unit() == gdp2.unit())
    # return CompareTimeSeries(gdp1, gdp2, "GDP")
    pass


@check_type_preconditions
def CompareTimeSeries(ts1: TimeSeries, ts2: TimeSeries, title: __String__) -> __Image__:
    # PythonPlotTwoLines(ts1.getValues(), ts1.getTime(), ts1.getLabel(),
    #                  ts2.getValues(), ts1.getTime(), ts2.getLabel(), title)
    pass

