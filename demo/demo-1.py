#!/usr/bin/env python3


#################################################
#
# KG
#
####################################################

class Entity:
    def __init__(self, name):
        self.name = name
        self.attrs = []

class Attr:
    def __init__(self, name):
        self.name = name

class Value:
    def __init__(self, v, t):
        self.v = v
        self.t = type(v)
    
class UnitedStates(Entity):
    def __init__(self):
        Entity.__init__(self, "United States")

class Canada(Entity):
    def __init__(self):
        Entity.__init__(self, "Canada")

class GDP(Attr):
    def __init__(self):
        Attr.__init__(self, "GDP")


# Entities from the KG
canada = Canada()
us = UnitedStates()

# Attrs in the KG
gdp = GDP()

#
# Facts in the KG!
#
# US GDP since 2010: https://www.thebalance.com/us-gdp-by-year-3305543, in trillions
# Canada GDP since 2010: https://www.thebalance.com/us-gdp-by-year-3305543, in trillions
#
kg = (
    (us, gdp, Value([15.59, 15.84, 16.19, 16.49, 16.91, 17.40, 17.68, 18.10, 18.63])),
    (canda, gdp, Value([1.61, 1.78, 1.82, 1.84, 1.80, 1.55, 1.52, 1.64, 1.70]))
    )
    

#################################################
#
# Action Graph
#
####################################################
class Action:
    def __init__(self, name):
        self.name = name

class Compare(Action):
    def __init__(self):
        Action.__init__(self, "Compare")

class Transmit(Action):
    def __init__(self):
        Transmit.__init__(self, "Transmit")

ag = (Compare(), Transmit())


#################################################
#
# Concrete Methods
#
####################################################
class ConcreteMethod:
    def __init__(self, name, numArgs, fn):
        self.name = name
        self.numArgs = numArgs
        self.fn = fn

class Plot(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Plot",
                                2,
                                lambda x, y: "Plot(" + str(x) + ", " + str(y) + ")")

class Transmit(ConcreteMethod):
    def __init__(self):
        ConcreteMethod.__init__(self,
                                "Transmit",
                                3,
                                lambda x, y, z: "Transmit(" + str(x) + ", " + str(y) + "," + str(z) + ")")


#################################################
#
# Refinements (I think it's a better name than Traits)
#
####################################################
class Refinement:
    def __init__(self, author, name, constraints):
        self.author = author
        self.name = name
        self.constraints = constraints

class RefinementConstraint:
    def __init__:
        pass

    def testParameterConstraint(p):
        """This method is invoked for every parameter sent to a method. It returns True if constraint is satisfied"""
        raise NotImplementedError()

    def testAllParametersConstraintOnValue(ps):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        raise NotImplementedError()

    def testAllParametersConstraintOnReference(ps):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        raise NotImplementedError()
        

class SameTypeConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same basic type"""
    def __init__(self):
        pass

    def testParameterConstraint(p):
        return True

    def testAllParametersConstraintOnValue(ps):
        """Test that all the parameters have the same basic type"""
        # This is the logic that a crowd worker might type in.  But it's pretty basic, so maybe we add it right away
        return len(set(map(lambda x: x.t, ps)) == 1

    def testAllParametersConstraintOnReference(ps):
        return True
    

class MustBeSameKGAttrConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same KG type"""
    def __init__(self):
        pass

    def testParameterConstraint(p):
        return True

    def testAllParametersConstraintOnValue(ps):
        return True

    def testAllParametersConstraintOnReference(ps):
        """Test that all the parameters are named via the same attribute"""
        # Again, pretty basic logic
        return len(set(map(lambda x: x[1], ps)) == 1


class ComparingTwoThings(Refinement):
    def __init__(self):
        Refinement.__init__(self, "Mike", "Comparing two things", (SameTypeConstraint(), MustBeSameKGAttrConstraint()))


#
# class ComparingGDP(Refinement):
#
# Not done yet....
    

userCode = (compare, [(us, gdp), (canada, gdp)])


#
# This method stands in for "The Compiler"
#
#
def kgcompile(userCode):
    # This is straightforward.  We need to pick a concrete method.
    concreteMethod = Plot()

    # We return a set of zero or more refinements that are applicable to the user code
    refinements = (ComparingTwoThings())

    #
    # We return a list of transformers, one for each parameter in the concrete method.
    #
    # A transformer is a function applied to the parameter supplied in the user code, which
    # turns the usercode parameter into something that can be supplied to the concrete method.
    #
    parameterTransformers = (lambda x: x.v, lambda x: x.v)
    
    return (userCode, concreteMethod, refinements, parameterTransformers)



compiledProgram = kgcompile(userCode)

metrics = computeQualityMetrics(compiledProgram)

userFacingResult = executeCompiledProgram(compiledProgram)

render(userFacingResult)


