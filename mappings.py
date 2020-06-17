class Mapping:
    """ Attributes:
            mapping (dict) : variable <--> value pairs.
    """
    def __init__(self, mapping, variables):
        """
            Args:
                mapping: a list.
                variables: a list.
        """
        self.mapping = {}
        for m, v in zip(mapping, variables):
            self.mapping[v] = m
    
    def __str__(self):
        tmp = [str(type(i)) for i in self.mapping.values()]
        return " ".join(tmp)