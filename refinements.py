from abc import ABC, abstractmethod

"""
    Each Refinement should contain attributes:
        description (str) (Q_R): A high-level description of the Refinement.
        method_desc (str) (R_C): A NL description of concrete method tied to the Refinement.
        mapping_desc (str) (R_M): Parameter mapping indications.
        involves (str) (Q_R): Description of what 'types' of things are involved in the Refinement.
"""

"""
    For now, let's assume only Refinments that implement all the above 4 attributes can be used.
"""

class Refinement(ABC):
    pass 


class Comparison(Refinement):
    description = "Comparison of two similar entities."


class HumanComparison(Comparison):
    description = "Comparison of two human beings."


class AmountComparison(Comparison):
    description = "Comparison of two set of quantity values."


class GDPComparison(AmountComparison):
    description = "Comparison of GDP values of two different places."
    invloves = ["GDP", "GDP"]
    method_desc = "PlotTwoLines"
    mapping_desc = ["GDP", "time"]
    # TODO: How about constraints such as same unit?

class PoliticianComparison(HumanComparison):
    description = "Comparison of two politicians."
    involves = ["Politician", "Politician"]
    method_desc = "PrintTexts"
    mapping_desc = ["political party"]