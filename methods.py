class ConcreteMethod(object):
    def __init__(self, name, args, fn):
        self.name = name
        self.fn = fn
        self.args = args

class Plot(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Plot",
                                {1:"x", 2:"y"},
                                lambda x, y: "Plot(" + str(x) + ", " + str(y) + ")"
                                )

class Transmit(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Transmit",
                                {1:"x", 2:"y", 3:"z"},
                                lambda x, y, z: "Transmit(" + str(x) + ", " + str(y) + "," + str(z) + ")",
                                )