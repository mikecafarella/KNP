import rdflib
from rdflib import Graph
from rdflib import store
from rdflib import Namespace
from rdflib import URIRef, BNode, Literal

g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
"""
kgtype = n.kgpltype
vid = n.val0
typ = Literal("kgplValue")
trip = (vid, kgtype, typ)
g.add(trip)
"""
server_url = "http://127.0.0.1:5000"
g.bind("kg", server_url + "/", override=False)
ns = Namespace(server_url + "/")
#url = ns["10"]
#print(url)
#qres = g.query(
#    """ASK {
#        ?x kg2:kgplType kg2:kgplValue .
#    }"""
#)
#for row in qres:
#    print(row)
# url = ns[str(10)]
# print(url)
# qres = g.query(
#         """SELECT ?ts ?val ?pyt
#         WHERE {
#             ?url kg:kgplType kg:kgplValue ;
#                kg:pyType ?pyt ;
#                kg:valueHistory ?ts .
#             ?ts kg:hasValue ?val .
#         }""",
#         initBindings={'url': url}
#     )
# print(len(qres))
# for a, b, c in qres:
#     print(type(a))
#     print(type(b))
#     print(type(c))
print(g.serialize(format='turtle').decode("utf-8"))
g.close()
