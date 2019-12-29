import utils

class Refinement:
    def __init__(self, author, name, constraints):
        self.author = author
        self.name = name
        self.constraints = constraints
    
    def __str__(self):
        return type(self).__name__

    def evaluate(self, IDs, method, mapping, KG_table, parameter_transformers):
        """This method evaluates all the RefinementConstraint."""
        valid_count = 0
        invalid_count = 0
        for constraint in self.constraints:
            v, inv = constraint.evaluate(IDs, method, mapping, KG_table, parameter_transformers)
            valid_count += v
            invalid_count += inv
        return (valid_count, invalid_count)


class RefinementConstraint:
    def __init__(self):
        pass

    @staticmethod
    def test_parameter_constraint(mapping, KG_table, parameter_transformers):
        """This method is invoked for every parameter sent to a method. It returns True if constraint is satisfied"""
        pass

    @staticmethod
    def test_all_parameters_constraint_on_value(mapping, KG_table, parameter_transformers):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        pass

    @staticmethod
    def test_all_parameters_constraint_on_reference(IDs):
        """This method is invoked once for all the parameters sent to a method. It returns True if constraint is satisfied"""
        pass

    @staticmethod
    def test_concrete_method(method):
        """Evaluate a logical test on the chosen concrete method"""
        pass

    def evaluate(self, IDs, method, mapping, KG_table, parameter_transformers):
        """Evaluate the constraints."""
        t1 = self.test_parameter_constraint(mapping, KG_table, parameter_transformers)
        t2 = self.test_all_parameters_constraint_on_value(mapping, KG_table, parameter_transformers)
        t3 = self.test_all_parameters_constraint_on_reference(IDs)
        t4 = self.test_concrete_method(method)
        t = (t1, t2, t3, t4)
        for test in t:
            if(test == False):
                utils.log_msg("{} failed!".format(type(self).__name__))
            elif(test == True):
                utils.log_msg("{} succeeded!".format(type(self).__name__))
        return (t.count(True), t.count(False))



class MustBeSameKGAttrConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same KG type."""

    @staticmethod
    def test_all_parameters_constraint_on_reference(IDs):
        """Test that all the parameters are named via the same attribute."""
        return len(set(map(lambda x: x[-1], IDs))) == 1


# class SameTypeConstraint(RefinementConstraint):
#     """This constraint means that all parameters must have the same basic type."""

#     @staticmethod
#     def test_all_parameters_constraint_on_value(mapping, KG_table, parameter_transformers):
#         """Test that all the parameters have the same basic type"""
#         # This is the logic that a crowd worker might type in.  But it's pretty basic, so maybe we add it right away
#         return len(set(map(lambda x: type(x), ps))) == 1


class SameUnitConstraint(RefinementConstraint):
    """This constraint means that  parameters must have the same unit."""

    @staticmethod
    def test_all_parameters_constraint_on_value(mapping, KG_table, parameter_transformers):
        set_of_units = set()
        for column in KG_table.columns:
            if(column.endswith(".unit")):
                set_of_units.update(KG_table[column].values)
        return len(set_of_units) == 1        


class ShouldDoPlottingConstraint(RefinementConstraint):
    """This constraint means a particular action should be taken"""

    @staticmethod
    def test_concrete_method(method):
        return "Compare" in method.actions_implemented


class ComparingTwoThings(Refinement):
    def __init__(self):
        Refinement.__init__(self, "Mike", "Comparing two things", (SameUnitConstraint(),
                                                                     MustBeSameKGAttrConstraint(),
                                                                     ShouldDoPlottingConstraint()))


class ComparingGDP(Refinement):
    def __init__(self):
        Refinement.__init__(self, "Mike", "Comparing GDP means making a time series",
                            (ShouldDoPlottingConstraint(),
                             SameUnitConstraint(),
                             MustBeSameKGAttrConstraint()))
