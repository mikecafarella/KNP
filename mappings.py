class Mapping:
    """ Attributes:
            mapping (dict) : variable -- value pairs.
            KG (str)
    """
    def __init__(self, KG=None, **kwargs):
        self.mapping = kwargs
        self.KG = KG