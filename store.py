import rdflib
from rdflib import Graph
from rdflib import store
from rdflib import Namespace
from rdflib import URIRef, BNode, Literal

g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg", "http://lasagna.eecs.umich.edu:80/")
"""
kgtype = n.kgpltype
vid = n.val0
typ = Literal("kgplValue")
trip = (vid, kgtype, typ)
g.add(trip)
"""
print(g.serialize(encoding="utf-8"))
g.close()
