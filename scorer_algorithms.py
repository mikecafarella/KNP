"""
    All functions here return a flot number in [0, 1]. The higher the score, the higher the probability.
"""

import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import utils
import re

def split_uppercase(value):
    return re.sub(r'([A-Z])', r' \1', value)


def _levenshtein_score(s1: str, s2: str):
    import Levenshtein
    return 1 - Levenshtein.distance(s1, s2) / max(len(s1), len(s2))


def _cosine_similarity(s1: str, s2: str):
    s1 = split_uppercase(s1)
    s2 = split_uppercase(s2)
    cleaned = [utils.clean_string(s1), utils.clean_string(s2)]
    vectorizer = CountVectorizer().fit_transform(cleaned)
    vectors = vectorizer.toarray()
    v1, v2 = vectors
    v1 = v1.reshape(1, -1)
    v2 = v2.reshape(1, -1)
    csim = cosine_similarity(v1, v2)[0][0]
    return csim

# _cosine_similarity("hello I am a student", "hi do you know that I was a student")
