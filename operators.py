

class Operator:
    pass


class Attribute:
    """ Attibute in an Operator.

    Use this class to create an attribute(flag) in an Operator.
    """

    __slots__ = ('_values', '_possible_values', '_name')

    def __init__(self, name, values, possible_values=None):
        self._name = name
        self._values = values
        if possible_values:
            self._possible_values = set().union(possible_values)
    
    def _add_possible_values(self, values):
        self._possible_values.union(values)
    

class Show(Operator):

    attributes = (
        Attribute('chart type', ('Boxplot', 'Scatterplot', 'Historgram', "Line Chart"), ('box plot', 'line_charts')),
        Attribute('method', ('PlotTwoLines'), ('two lines')),
        Attribute('output type', ('Image', 'Chart', 'Text'))
    )


class Transform(Operator):
    pass