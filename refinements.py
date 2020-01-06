import utils

class Refinement:
    def __init__(self, author, name, constraints):
        self.author = author
        self.name = name
        self.constraints = constraints
        self.evaluation_results = {}
    
    def __str__(self):
        return type(self).__name__

    def evaluate(self, IDs, method, mapping, KG_tables, parameter_transformers):
        """This method evaluates all the RefinementConstraint."""

        for constraint in self.constraints:

            rst = constraint.evaluate(IDs, method, mapping, KG_tables, parameter_transformers)
            if rst == True:
                self.evaluation_results[str(constraint)] = True
            elif rst == False:
                self.evaluation_results[str(constraint)] = False

        return self.evaluation_results


class RefinementConstraint:
    def __init__(self):
        pass

    def __str__(self):
        return type(self).__name__

    @staticmethod
    def test_parameter_constraint(mapping, KG_tables, parameter_transformers):
        """This method is invoked for every parameter sent to a method. It returns True if constraint is satisfied"""
        pass

    @staticmethod
    def test_all_parameters_constraint_on_value(mapping, KG_tables, parameter_transformers):
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

    def evaluate(self, IDs, method, mapping, KG_tables, parameter_transformers):
        """Evaluate the constraints."""
        t1 = self.test_parameter_constraint(mapping, KG_tables, parameter_transformers)
        t2 = self.test_all_parameters_constraint_on_value(mapping, KG_tables, parameter_transformers)
        t3 = self.test_all_parameters_constraint_on_reference(IDs)
        t4 = self.test_concrete_method(method)
        t = (t1, t2, t3, t4)
        if t.count(None) != 3:
            raise AssertionError("One constraint could only implement one test.")
        for test in t:
            if(test == False):
                utils.log_msg("{} failed!".format(str(self)))
                return False
            elif(test == True):
                utils.log_msg("{} succeeded!".format(str(self)))
                return True



class MustBeSameKGAttrConstraint(RefinementConstraint):
    """This constraint means that all parameters must have the same KG type."""

    @staticmethod
    def test_all_parameters_constraint_on_reference(IDs):
        """Test that all the parameters are named via the same attribute."""
        return len(set(map(lambda x: x[-1], IDs))) == 1


# class SameTypeConstraint(RefinementConstraint):
#     """This constraint means that all parameters must have the same basic type."""

#     @staticmethod
#     def test_all_parameters_constraint_on_value(mapping, KG_tables, parameter_transformers):
#         """Test that all the parameters have the same basic type"""
#         # This is the logic that a crowd worker might type in.  But it's pretty basic, so maybe we add it right away
#         return len(set(map(lambda x: type(x), ps))) == 1


class SameUnitConstraint(RefinementConstraint):
    """This constraint means that  parameters must have the same unit."""

    @staticmethod
    def test_all_parameters_constraint_on_value(mapping, KG_tables, parameter_transformers):
        try:
            set_of_units = set()
            for _, df in KG_tables.items():
                for column in df['columns']:
                    if(column.endswith(".unit")):
                        set_of_units.update(df[column].values)
            return len(set_of_units) == 1
        except:
            return False   


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
