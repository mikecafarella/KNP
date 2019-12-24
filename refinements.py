class Refinement:
    def __init__(self, author, name, constraints):
        self.author = author
        self.name = name
        self.constraints = constraints


class RefinementConstraint:
    def __init__(self):
        pass

    def testParameterConstraint(p):
        """This method is invoked for every parameter sent to a method. It returns True if constraint is satisfied"""
        return True

    def testAllParametersConstraintOnValue(ps):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        return True

    def testAllParametersConstraintOnReference(ps):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        return True

    def testConcreteMethod(self, concreteMethod):
        """Evaluate a logical test on the chosen concrete method"""
        return True


class MustBeSameKGAttrConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same KG type."""

    def testAllParametersConstraintOnReference(ps):
        """Test that all the parameters are named via the same attribute"""
        # return (len(set(map(lambda x: x[1], ps)) == 1)
        pass


class SameTypeConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same basic type."""
    def testAllParametersConstraintOnValue(ps):
        """Test that all the parameters have the same basic type"""
        # This is the logic that a crowd worker might type in.  But it's pretty basic, so maybe we add it right away
        # return len(set(map(lambda x: x.t, ps)) == 1
        pass


class ComparingTwoThings(Refinement):
    def __init__(self):
        Refinement.__init__(self, "Mike", "Comparing two things", (SameTypeConstraint(), MustBeSameKGAttrConstraint()))


class ComparingGDP(Refinement):
    def __init__(self):
        Refinement.__init__(self, "Mike", "Comparing GDP means making a time series",
                            (ShouldDoPlottingConstraint,
                             ShouldHaveSameCurrencyConstraint,
                             ShouldBeInflationAdjustedConstraint))


        

# class ShouldDoPlottingConstraint(RefinementConstraint):
#     """This constraint means a particular action should be taken"""
#     def __init__(self):
#         pass

#     def testConcreteMethod(self):
#         return ctsPlot in concreteMethod.actionsImplementeds