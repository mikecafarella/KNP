from abc import ABC, abstractmethod
#
# All following functions assuming using Wikidata Schema
#
from typing import List, Set, Mapping, Tuple
import pandas as pd
import copy
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import random
import numpy as np
import joblib
import os

from .embeddings import wembedder
vector = wembedder.model.wv.word_vec


from query import IR
from scorer_algorithms import _cosine_similarity

MODEL_CACHE_DIR = ".cache/"


class Type(ABC):
    """Attrs:
            type (str): 'entiy' or 'relation' or 'built_in'.
            pos_examples (list): a list of Wikidata ID representing the pos_examples of the Type.
            neg_examples (list): a list of Wikidata ID."""

    @classmethod
    def train_classifier(cls):
        neg_pos_ratio = 1
        X = [wembedder.model.wv.word_vec(x) for x in cls.pos_examples if x in wembedder.model.wv.vocab]
        if len(X) != len(cls.pos_examples):
            print("Alert: there are {} embeddings of pos_examples not found!".format(len(cls.pos_examples) - len(X)))
        if hasattr(cls, "neg_exampls"):
            X_neg = [wembedder.model.wv.word_vec(x) for x in cls.neg_examples if x in wembedder.model.wv.vocab]
            if len(X_neg) != len(cls.neg_examples):
                print("Alert: there are {} embeddings of neg_examples not found!".format(len(cls.pos_examples) - len(X)))
        else:
            X_neg = []
        y = np.zeros((neg_pos_ratio+1) * len(X))
        y[0:len(X)] = 1
        while len(X_neg) < neg_pos_ratio * len(X):
            QID, vec = random.choice(list(wembedder.model.wv.vocab.items())) 
            # cls.neg_examples.append(QID)
            X_neg.append(wembedder.model.wv.word_vec(QID))
        X += X_neg
        # clf = LogisticRegression(random_state=0, class_weight='balanced').fit(X, y)
        clf = svm.SVC(probability=True).fit(X, y)
        cls.clf = clf

    @classmethod
    def typefunc(cls, X):
        """
            Args:
                X: a KGPLValue.
            return:
                 a float in [0, 1] representing the possbiility of X is a memboer of the type.
        """
        if hasattr(X, "val"):
            X = X.val
        else:
            raise RuntimeError("X must be a KGPLValue!")
        if cls.type == 'entity':
            if hasattr(cls, "pos_examples") and not hasattr(cls, "clf"):
                if not os.path.exists(MODEL_CACHE_DIR + cls.__name__):
                    if not os.path.exists(MODEL_CACHE_DIR):
                        os.mkdir(MODEL_CACHE_DIR)
                    cls.train_classifier()
                    joblib.dump(cls.clf, MODEL_CACHE_DIR + cls.__name__)
                else:
                    cls.clf = joblib.load(MODEL_CACHE_DIR + cls.__name__)

            # if isinstance(X, str):
            #     v = vector(X)
            #     return cls.clf.predict_proba([v])[0][1]
            
            if isinstance(X, IR):
                if X.focus is not None:
                    # TODO: how about Obama.wife?
                    return 0
                else:
                    v = vector(X.id)
                    return cls.clf.predict_proba([v])[0][1]
            else:
                raise ValueError("Unsuported X!")
        elif cls.type == 'relation':
            if isinstance(X, str):
                raise ValueError("Unimplemented! Not supposed to use this.")
            elif isinstance(X, IR):
                if X.focus is None:
                    return 0
                focus_label = X.focus_label
                return _cosine_similarity(focus_label, cls.__name__)
            else:
                raise ValueError("Unsuported X!")
        elif cls.type == 'built_in':
            pass
        else:
            raise ValueError("Unsuported type!")
        

# def _match(schema: Mapping[str, Type], source) -> Mapping:
#     """ 
#         Deprecated.
#     """
#     rst = {}
#     scores = []
#     # columns = list(df.columns)
#     # if len(columns) < len(schema):
#     #     return None, 0
#     # for s in schema:
#     #     columns.sort(key=lambda col_name: scorer_algorithms._levenshtein_score(col_name, s))
#     #     column = columns.pop()
#     #     rst[s] = df[column]
#     #     scores.append(scorer_algorithms._levenshtein_score(column, s))
#     if isinstance(source, query.IR):
#         possible_matches = {}
#         for pid, df in source.properties.items():
#             for column in df.columns:
#                 possible_matches[pid + "." + str(column)] = df[column]

#         print(possible_matches.keys())

#         source_labels = list(possible_matches.keys())

#         for target_label, _type in schema.items():
#             if _type is __List__:
#                 # source_labels = list(possible_matches.keys())
#                 source_labels.sort(key=lambda source_label: scorer_algorithms._levenshtein_score(source_label, target_label))
#                 # tmp = source_labels.pop()
#                 tmp = source_labels[-1]
#                 rst[target_label] = possible_matches[tmp]
#                 scores.append(scorer_algorithms._levenshtein_score(tmp, target_label))
#             elif _type is __String__:
#                 # source_labels = [l.split(".")[1:] for l in list(possible_matches.keys())]
#                 source_labels.sort(key=lambda source_label: scorer_algorithms._levenshtein_score(source_label, target_label))
#                 # tmp = source_labels.pop()
#                 tmp = source_labels[-1]
#                 rst[target_label] = tmp
#                 scores.append(scorer_algorithms._levenshtein_score(tmp, target_label))
#             else:
#                 raise ValueError("Not implemented yet")
#     elif isinstance(source, Type):
#         if source.schema == schema:
#             return copy.deepcopy(source.attributes), 1  # TODO: source.overall_score?
#         # for label, _type in schema.items():
#         #     pass
#         raise ValueError("Not implemented yet")
#     else:
#         raise ValueError("Not implemented yet")
#     return rst, sum(scores) / len(scores)


# def check_instanceOf_prop(IR, entity_id: str):
#     """ 
#         Deprecated.
#     """
#     """ Chechk if the entity represented by IR is an instance of the entity with entity_id."""
#     PID = 'P31'
#     if PID not in IR.properties:
#         return 0
#     series = IR[PID]["wikidata ID"]
#     if entity_id in series:
#         return 1
#     return 0


# def check_occupation_prop(IR, entity_id: str):
#     """ 
#         Deprecated.
#     """
#     PID = "P106"
#     if PID not in IR.properties:
#         return 0
#     series = IR[PID]["wikidata ID"]
#     if entity_id in series:
#         return 1
#     return 0


# def check_prop(IR, prop_id: str):
#     """ 
#         Deprecated.
#     """
#     if IR.focus == prop_id:
#         return 1
#     else:
#         return 0
