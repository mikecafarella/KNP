import rdflib
from rdflib import Graph
from rdflib import store
from rdflib import Namespace
from rdflib import URIRef, BNode, Literal
import requests
import kgpl
"""
g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)

print(g.serialize(format='xml').decode("utf-8"))


print(l)
g.close()
"""
a = kgpl.value(12)