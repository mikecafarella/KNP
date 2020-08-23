from rdflib import Graph, Literal
from rdflib import Namespace
import kgpl

def test1():
    # server_url = "http://127.0.0.1:5000"
    server_url = "http://global.url"  # The namespace, should be adjusted on every server
    g = Graph('Sleepycat', identifier="kgpl")
    g.open('db_test', create=True)
    g.bind("kg", server_url + "/")
    ns = Namespace(server_url + "/")

    # predicates
    hasHistory = ns.hasHistory
    hasKGPLValue = ns.hasKGPLValue
    valueHistory = ns.valueHistory
    hasValue = ns.hasValue
    kgplType = ns.kgplType
    pyType = ns.pyType

    # kgplType
    kgplValue = ns.kgplValue
    kgplVariable = ns.kgplVariable

    url = ns["val/" +str(10)]
    val= Literal(10)
    g.add((url, hasValue, val))
    g.add((url, kgplType, kgplValue))

    val_url = ns["val/"+str(10)]
    qres = g.query(
        """ASK {
            {?url kg:kgplType kg:kgplValue}
            }
        """,
        initBindings={'url': val_url}
    )
    print(qres)
    for x in qres:
        print(x)

def test2():
    my_test_string = "First Value."
    myval = kgpl.value(my_test_string)
    kgpl.variable(myval.vid)

if __name__ == "__main__":
    test2()