from .core import Type


class Image(Type):
    type = 'built_in'

    @classmethod
    def typefuc(cls, X):
        raise NotImplementedError("")


class List(Type):
    type = 'built_in'

    @classmethod
    def typefuc(cls, X):
        raise NotImplementedError("")


class String(Type):
    type = 'built_in'
    
    @classmethod
    def typefuc(cls, X):
        if hasattr(X, "val"):
            X = X.val
        return isinstance(X, str)


class Integer(Type):
    type = 'built_in'

    @classmethod
    def typefuc(cls, X):
        if hasattr(X, "val"):
            X = X.val
        return isinstance(X, int)


# class TimeSeries(Type):
    
    # def __init__(self, source):
    #     # if isinstance(source, query.IR):
    #     #     source = source.properties
    #     #     # IR = source
    #     #     # if IR.focus is not None:
    #     #     #     source = IR[IR.focus]
    #     #     # else:
    #     #     #     #
    #     #     #     # For now, let's assume the user won't pass an entire entity to convert to TimeSeries
    #     #     #     #
    #     #     #     raise RuntimeError("Should never do this!")
    #     # elif isinstance(source, Type):
    #     #     # TODO: the source might already be TimeSeries
    #     #     source = source.attributes
    #     # else:
    #     #     self.overall_score = 0
    #     #     return

    #     self.attributes, self.overall_score = _match(self.schema, source)
    #     assert(len(self.attributes.keys()) == len(self.schema.keys()))
        
        
        

class MovieStar(Type):
    type = "entity"
    pos_examples = ["Q35332",
                    "Q40523",
                    "Q4616",
                    "Q40096"]


class Politician(Type):
    type = "entity"
    pos_examples = ["Q76",  # Barack Obama
                    "Q6279",  # Joe Biden
                    "Q22686",  # Donald Trump
                    "Q9960"  # Ronald Reagan
                    ]
    

class Country(Type):
    type = "entity"
    pos_examples = ["Q30",  # USA
                    "Q148",  # China
                    "Q17",  # Japan
                    "Q145"  # UK
                    ]

class State(Type):
    type = "entity"
    pos_examples = ["Q1166",  # Michigan
                    "Q771",  # Massachusetts
                    "Q99",  # California
                    "Q812"  # Florida
                    ]


class Place(Type):
    type = "entity"
    pos_examples = ["Q1166",  # Michigan
                    "Q771",  # Massachusetts
                    "Q99",  # California
                    "Q812",  # Florida
                    "Q30",  # USA
                    "Q148",  # China
                    "Q17",  # Japan
                    "Q145",  # UK
                    "Q1297",
                    "Q65", 
                    "Q484678",
                    "Q49149"
                    ]

class LifeExpectancy(Type):
    type = "relation"