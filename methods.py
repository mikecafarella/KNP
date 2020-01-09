import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

import pandas as pd

class ConcreteMethod(object):
    def __init__(self, name, num_args, type_checks, actions_implemented, output_type):
        self.name = name
        self.type_checks = type_checks
        self.num_args = num_args
        self.actions_implemented = actions_implemented
        self.output_type = output_type
    
    def __str__(self):
        return "{} takes {} arguments, outputs {}.".format(self.name, self.num_args, self.output_type)

    def function(*args):
        pass


class Plot(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Plot",
                                4,
                                {1: lambda x: all(isinstance(y, (int, float)) for y in x), 
                                    2: lambda x: all(isinstance(y, (int, float)) for y in x),
                                    3: lambda x: isinstance(x, str),
                                    4: lambda x: isinstance(x, str)},
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
        super().__init__("PlotTwoLines", 8, {}, ["Compare"], "image")

    @staticmethod
    def function(*args):
        
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(args[0], args[1], label=args[2])
        ax.plot(args[3], args[4], label=args[5])
        plt.xlabel(args[-2])
        plt.ylabel(args[-1])
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