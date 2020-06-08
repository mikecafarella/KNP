import pickle

import sqlalchemy
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base
import kgpl
import KNPSStore
engine = create_engine('sqlite:///KGPLData.db', echo=False)

Session = sessionmaker(bind=engine)
s = Session()

if __name__ == '__main__':
    val1 = kgpl.KGPLStr("val1 str")
    val2 = kgpl.KGPLInt(42)
    valn = kgpl.KGPLStr("should not in local or remote database")

    var1 = kgpl.KGPLVariable(val1)
    var2 = kgpl.KGPLVariable(val2)
    print("+++")
    print(val1.__repr__())
    print("+++")
    print(val2.__repr__())
    print("+++")
    print(var1.__repr__())
    print("+++")
    print(var2.__repr__())
    #
    var1.registerVariable()
    var2.registerVariable()
    # # # print(var1.__repr__())
    # # # print(var2.__repr__())
    var1.reassign(val2)
    # # print(val1.__repr__())
    # # print(val2.__repr__())
    # print("+++")
    # print(var1.__repr__())
    # print("+++")
    # print(var2.__repr__())

    store = KNPSStore.KNPSStore('http://lasagna.eecs.umich.edu:8080')
    var3 = store.GetVariable("V2")
    print("+++")
    print(var3.__repr__())
    var4 = store.GetVariable("V1")
    print("+++")
    print(var4.__repr__())

    # # var1 = kgpl.KGPLVariable("var2-uuid")
    #
    #
    #
    # # print(var1.__repr__())
    # # var1.registerVariable()
    #
    #
    #
    # # test_store = KNPSStore.KNPSStore(None)
    # # # test_store.GetVariable("V2")
    # #
    # # print(var1)
    # # print(var1.timestamp)
    # # var1.reassign(val2.id)
    # #
    # # print(var1)
    # # print(var1.timestamp)
