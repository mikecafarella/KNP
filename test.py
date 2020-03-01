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

# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import HashingVectorizer

# corpus = [
#     'This is the first document.',
#     'This document is the second document.',
#     'And this is the third one.',
#     'Is this the first document?',
# ]
# vectorizer = HashingVectorizer(analyzer='word',ngram_range=(2,2), n_features=2**4)
# X = vectorizer.fit_transform(corpus)
# print(vectorizer.get_feature_names())
# new_corpus = ["this"]
# Y = vectorizer.transform(new_corpus)
# print(Y.toarray())
# print(list(X.toarray()[0]))

# A = [1, 2]
# B = ['v1', 'v2']
# for e in itertools.product(A, B, repeat=2):
#     if e[1] == e[3]:
#         continue
#     print(e)

# def permutations(iterable, r=None):
#     pool = tuple(iterable)
#     n = len(pool)
#     r = n if r is None else r
#     for indices in itertools.product(range(n), repeat=r):
#         # print(indices)
#         if len(set(indices)) == r:
#             print(indices)
#             yield tuple(pool[i] for i in indices)

# # print(range([1,2,3]))
# for e in permutations([1,2,3], r=2):
#     continue
#     print(e)

# import seaborn as sns

# print(sns.get_dataset_names())
# # print(sns.load_dataset("anscombe"))

# import utils

# for e in utils.generate_mappings(['v1', 'v2'], ['a', 'b', 'c'], 3):
#     # continue
#     print(e)


# df = utils.load_seaborn_dataset('iris')
# # utils.test_mappings(methods.OneNumericSeveralGroupBoxPlot, df)


# actual_mapping = (df["species"], df["sepal_length"])

# method=methods.OneNumericSeveralGroupBoxPlot
# with open("test.yml", 'r') as f:
#     data = yaml.load(f)
# print(data)

# print(utils.parse("Operator([d1, d2],a,2,3)"))

# def t(a, b ,c):
#     print(a, b, c)

# data = {"a":1, "c":3, "b":2}
# t(**data)

# # data = pd.DataFrame({"a":[1], "b":[2]})
# # print(data['a'].name)
# a = [1, 2]
# print(max(a))

# a = [1, 2, 3]
# print(a[0:2])

# import rdflib
# g = rdflib.Graph()
# g.parse("/Users/yuzelou/Downloads/Q42.nt", format="ttl")


# print(len(g))
# import pprint
# for stmt in g:
#     pprint.pprint(stmt)
#     break

from wikidata_utils import *

# claims = get_claims("Q76", "P19")

# print(claims[0]["mainsnak"]["datavalue"]["value"]["id"])

import query

# ir = query.IR("Q76", "wikidata")
# print(ir["abc"])
# obj = get_entity("Q30")
# # print([m["value"] for m in obj["aliases"]["en"]])
# claims = obj["claims"]
# for p_id, mainsnaks in claims.items():
#     print(p_id)
#     for mainsnak in mainsnaks:
#         print(mainsnak.keys())
#     break
# d = {'col1': [1], 'col5': [[3, 4]]}
# df = pd.DataFrame(data=d)
# print(df)
# df2 = pd.DataFrame({'col1':[3], 'col3':[4]})

# df = df.append(df2, ignore_index=True, sort=True)
# print(df)

# query.IR("Q30", "wikidata", focus="P40")

# a = {'wikidata ID': ['Q15070048'], 'wikidata entity type': ['item'], 'label': ['Sasha Obama'], 'description': ['daughter of former US President Barack Obama and Michelle Obama'], 'aliases': [['Q15070048']], 'url': ['www.wikidata.org/wiki/Q15070048']}
# b = {'wikidata ID': 'Q15070044', 'wikidata entity type': 'item', 'label': ['Malia Obama'], 'description': ['daughter of former US President Barack Obama and Michelle Obama'], 'aliases': [['Q15070044']], 'url': ['www.wikidata.org/wiki/Q15070044']}
# data_df = pd.DataFrame(data=a)
# print(data_df)

# data_df = data_df.append(b, ignore_index=True, sort=True)
# d = {"a":1, "b":2, "c": [1,2]}
# df = pd.DataFrame.from_records(d)
# print(df)

# m = methods.AreaChart()
# # print(q['Q30.P2131']['P2131'])
# core.generate_parameter_mappings(q, m)
# df1 = pd.DataFrame({"a":[1,2,3], "b":[4,5,6]})
# m = methods.BasicScatterPlot()
# print(df1["a"])
# m.function(df1["a"], df1["b"])
# print(inspect.signature(methods.PrintTexts.function).parameters.keys())
import pprint
q = query.Query("ShowMeAPlot(['Q30.P2131'])", KG="wikidata")
candidate_invocations = core.process_query(q, rank=5)  # could add a keyword 'limit' here to limits the max number of candidate invocations
for inv in candidate_invocations:
    print(inv.score)
    pprint.pprint(inv.m.mapping)
    print()
    print()
    print()
# df = pd.DataFrame({"time":[1,2,3], "amount":[4,5,6]})
# x = df['time']
# y = df['amount']

# print(x)
# m = {"x":x, "y":y}
# c = getattr(methods, "BasicScatterPlot")()
# c.function(**m)