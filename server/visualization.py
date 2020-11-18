#!/usr/bin/env python3
import rdflib
import pprint

if __name__ == "__main__":
    g = rdflib.Graph('Sleepycat', identifier="kgpl")
    g.open('db', create=True)
    # for stmt in g:
    #     pprint.pprint(stmt)
    g.serialize("kgpl.ttl", format="turtle")
    g.close()

    g = rdflib.Graph('Sleepycat', identifier="dependency")
    g.open('db', create=True)
        # for stmt in g:
        #     pprint.pprint(stmt)
    g.serialize("dependency.ttl", format="turtle")
    g.close()