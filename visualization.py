import rdflib
import pprint

if __name__ == "__main__":
    g = rdflib.Graph('Sleepycat', identifier="dependency")
    g.open('db', create=True)
    # for stmt in g:
    #     pprint.pprint(stmt)
    g.serialize("dg.ttl", format="turtle")
    g.close()