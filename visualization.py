import rdflib
import pprint

if __name__ == "__main__":
    g = rdflib.Graph('Sleepycat', identifier="kgpl")
    g.open('db', create=True)
    # for stmt in g:
    #     pprint.pprint(stmt)
    g.serialize("parent_test.ttl", format="turtle")
    g.close()