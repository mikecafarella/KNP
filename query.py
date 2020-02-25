import utils

class Query:
    """ The class for user queries.

        Args:
            raw_query (string): the raw string the user typed.

        Attributes:
            raw_query: the raw string the user typed.
            operator_desc (str): A string describes the tast, could be used to match Refinements.
            pos_args (list): positinal arguments in the query.
            keyword_args (list): keyword arguments in the query.
            datasets (list[DataFrame]):
            KG_params (List)
    """
    def __init__(self, raw_query):
        self.raw_query = raw_query
        self._parse_user_query()
    
    def _parse_user_query(self, KG=None):
        """
        Fow now: assume the user uses a dataset from seaborn by passing the dataset name
            as the first argument in the query string.
        """
        operator_desc, first_params, pos_args, keyword_args = utils.parse(self.raw_query)
        self.operator_desc = operator_desc
        self.pos_args = pos_args
        self.keyword_args = keyword_args
        self.first_params = first_params
        if KG is None:
            self.datasets = [utils.load_seaborn_dataset(dataset_name) for dataset_name in first_params]
        else:
            self.KG_params = first_params