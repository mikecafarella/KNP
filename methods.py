

import pandas as pd
import inspect
from abc import ABC, abstractmethod


class ConcreteMethod(ABC):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

    @abstractmethod
    def function():
        pass

    def get_variables(self):
        return inspect.signature(self.function)

    def get_types(self):
        return set()


class PlotTwoLines(ConcreteMethod):
    def __init__(self):
        super().__init__("PlotTwoLines")

    def get_types(self):
        return set(["/code/TimeSeriesPlot"])

    @staticmethod
    def function(x_value_1, y_value_1, legend_1, x_value_2, y_value_2, legend_2, xlabel, ylabel):

        import matplotlib
        import matplotlib.pyplot as plt
        # matplotlib.use('agg')
        
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(x_value_1, y_value_1, label=legend_1)
        ax.plot(x_value_2, y_value_2, label=legend_2)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        ax.legend()

        plt.show()
        # return fig


class BasicLineChart(ConcreteMethod):
    def __init__(self):
        super().__init__("BasicLineChart")

    def get_types(self):
        return set(["/code/TimeSeriesPlot"])

    @staticmethod
    def function(values):

        import matplotlib.pyplot as plt
        import numpy as np

        plt.plot(values)

        plt.show()


class OneNumericBoxPlot(ConcreteMethod):
    def __init__(self):
        super().__init__("OneNumericBoxPlot")

    def get_types(self):
        return set(["/code/BoxPlot"])

    @staticmethod
    def function(y):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.boxplot( y=y )

        plt.show()


class OneNumericSeveralGroupBoxPlot(ConcreteMethod):
    def __init__(self):
        super().__init__("OneNumericSeveralGroupBoxPlot")

    def get_types(self):
        return set(["/code/BoxPlot"])
    
    @staticmethod
    def function(x, y):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.boxplot( x=x, y=y )

        plt.show()


class BasicScatterPlot(ConcreteMethod):
    def __init__(self):
        super().__init__("BasicScatterPlot")

    def get_types(self):
        return set(["/code/ScatterPlot"])

    @staticmethod
    def function(x, y):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.regplot(x=x, y=y, fit_reg=False)

        plt.show()


class BasicHistogram(ConcreteMethod):
    def __init__(self):
        super().__init__("BasicHistogram")

    def get_types(self):
        return set(["/code/Histogram"])
    
    @staticmethod
    def function(x):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.distplot( x )

        plt.show()


class AreaChart(ConcreteMethod):
    def __init__(self):
        super().__init__("AreaChart")
    
    @staticmethod
    def function(x, y):
        import matplotlib.pyplot as plt

        plt.fill_between(x, y)


        plt.show()


class DensityPlot(ConcreteMethod):
    def __init__(self):
        super().__init__("DensityPlot")
    
    @staticmethod
    def function(values):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.kdeplot(values)

        plt.show()


class BubblePlot(ConcreteMethod):
    def __init__(self):
        super().__init__("BubblePlot")
    
    @staticmethod
    def function(x, y, z):
        import seaborn as sns
        import matplotlib.pyplot as plt

        plt.scatter(x, y, s=z*1000, alpha=0.5)
        plt.show()


class BasicViolinPlot(ConcreteMethod):
    def __init__(self):
        super().__init__("BasicViolinPlot")
    
    @staticmethod
    def function(y):
        import seaborn as sns
        import matplotlib.pyplot as plt

        sns.violinplot( y=y )
        plt.show()


class PrintTexts(ConcreteMethod):
    def __init__(self):
        super().__init__("PrintTexts")

    def get_types(self):
        return set(["/code/Text"])
    
    @staticmethod
    def function(*texts):
        for text in texts:
            print(text)

class TableGen(ConcreteMethod):
    def __init__(self):
        super().__init__("TableGen")

    def get_types(self):
        return set(["/code/TableGenMethod"])
    
    @staticmethod
    def function(*texts):
        for text in texts:
            print(text)
