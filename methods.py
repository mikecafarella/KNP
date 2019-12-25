import matplotlib.pyplot as plt

class ConcreteMethod(object):
    def __init__(self, name, num_args, type_checks):
        self.name = name
        self.type_checks = type_checks
        self.num_args = num_args
    
    def function(*args):
        pass


class Plot(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Plot",
                                4,
                                {1: lambda x: all(isinstance(y, (int, float)) for y in x), 
                                    2: lambda x: all(isinstance(y, (int, float)) for y in x),
                                    3: lambda x: isinstance(x, string),
                                    4: lambda x: isinstance(x, string)}
                                )

    @staticmethod
    def function(*args):
        
        arg_1, arg_2, arg_3, arg_4 = args
        plt.plot(arg_1, arg_2)
        plt.xlabel(arg_3)
        plt.ylabel(arg_4)
        plt.show()

        


class Transmit(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Transmit",
                                3,
                                {}
                                )