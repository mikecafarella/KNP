import pandas as pd
import itertools
import inspect
# import methods
# import utils
from threading import Thread
import yaml
import methods
import utils
import core
import query

import pprint
q = query.Query("ShowMeAPlot(['Q30.P2131'])", KG="wikidata")
candidate_invocations = core.process_query(q, rank=5)  # could add a keyword 'limit' here to limits the max number of candidate invocations
for inv in candidate_invocations:
    print(inv.score)
    pprint.pprint(inv.m.mapping)
    print()
    print()
    print()
