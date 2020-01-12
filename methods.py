import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

import pandas as pd

class ConcreteMethod(object):
    def __init__(self, name, num_args, actions_implemented, output_type):
        self.name = name
        self.num_args = num_args
        self.actions_implemented = actions_implemented
        self.output_type = output_type
    
    def __str__(self):
        return self.name

    def function(*args):
        pass


class Plot(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Plot",
                                4,
                                ["Show"],
                                "image"
                                )

    @staticmethod
    def function(*args):

        arg_1, arg_2, arg_3, arg_4 = args
        plt.plot(arg_1, arg_2)
        plt.xlabel(arg_3)
        plt.ylabel(arg_4)
        plt.show()

class PlotTwoLines(ConcreteMethod):
    def __init__(self):
        super().__init__("PlotTwoLines", 8, ["Compare"], "image")

    @staticmethod
    def function(x_value_1, y_value_1, legend_1, x_value_2, y_value_2, legend_2, xlabel, ylabel):
        
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(x_value_1, y_value_1, label=legend_1)
        ax.plot(x_value_2, y_value_2, label=legend_2)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        ax.legend()
        # plt.show()
        return fig
        


class Transmit(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Transmit",
                                3,
                                {}
                                )