from time import sleep
import rdflib
import kgpl
import pprint

if __name__ == "__main__":

    node_a = kgpl.value("node A")
    node_b = kgpl.value("node B")

    my_edge = "parentOf" # Edges names are assumed to have no spaces in between
    kgpl.set_edge(node_a, node_b, my_edge)

    g = rdflib.Graph('Sleepycat', identifier="kgpl")
    g.open('db', create=True)
    for stmt in g:
        pprint.pprint(stmt)
    g.serialize("parent_test.ttl", format="turtle")
    g.close()
