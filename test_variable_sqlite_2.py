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
    # should NOT be able to see value 2 in server db and local db at this time
    var1 = kgpl.KGPLVariable(val1)
    print("+++")
    print(val1.__repr__())
    print("+++")
    print(val2.__repr__())
    print("+++")
    print(var1.__repr__())

    var1.registerVariable()
    var1.reassign(val2)
    # should be able to see value 2 in server db and local db at this time
