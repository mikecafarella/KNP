from rdflib import Graph, Literal
from rdflib import Namespace
import kgpl
from datetime import datetime, timedelta


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

    url = ns["val/" + str(10)]
    val = Literal(10)
    g.add((url, hasValue, val))
    g.add((url, kgplType, kgplValue))

    val_url = ns["val/" + str(10)]
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
    """Now we force comment to be existed!"""
    my_test_string = "First Value."
    myval = kgpl.value(my_test_string)
    kgpl.variable(myval.vid)

def test3():
    my_test_string = "First Value."
    my_test_comment = "value comment 1"
    my_test_comment2 = "variable comment 1"
    myval = kgpl.value(my_test_string, my_test_comment)
    kgpl.variable(myval.vid, my_test_comment2)


def test3_1():
    my_test_string = "Second Value."
    my_test_comment = "value comment 2."
    # my_test_comment2 = "variable comment 2."
    myval = kgpl.value(my_test_string, my_test_comment)
    # kgpl.variable(myval.vid, my_test_comment2)




def test4():
    print(datetime.today())

def test5():
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
    print(ns["/var/1"])
    print(type(ns["/var/1"]))

def test6():
    test_load_val = kgpl.load_val("http://127.0.0.1:5000/val/0")
    test_load_var = kgpl.load_var("http://127.0.0.1:5000/var/0")
    print(test_load_val)

def test7():
    test_load_val = kgpl.load_val("http://127.0.0.1:5000/val/1")
    test_load_var = kgpl.load_var("http://127.0.0.1:5000/var/0")
    kgpl.set_var(test_load_var, test_load_val.vid, "reassign to val 1")
    print("place holder")

def test8():
    test_load_var = kgpl.load_var("http://127.0.0.1:5000/var/0")
    his = kgpl.get_history(test_load_var)
    print(his)
    print("place holder")

def test9():
    kgpl.viewNamespace()
    kgpl.changeNamespace("http://global//")
    kgpl.viewNamespace()

if __name__ == "__main__":
    test3() # Create new KGPLValues and KGPLVariables
    test3_1() # Create another KGPLValue
    # test6() # Load val and var
    test7() # reassign
    # test8() # get history
    # test9() # test Namespace changes
