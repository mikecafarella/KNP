import pickle

from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import kgpl
from random import choice
import KNPSStore as Store

# from string import letters

# engine = create_engine('sqlite:///KGPLData.db', echo=True)
engine = create_engine('sqlite:///KGPLData.db', echo=False)

Session = sessionmaker(bind=engine)
s = Session()

# con = engine.raw_connection()

if __name__ == '__main__':  # If run twice, it will insert twice.
    print(type(type(kgpl.KGPLInt(42))))
    print(type(kgpl.KGPLInt(42)))
    my_string = type(kgpl.KGPLInt(42)).__name__
    print(my_string)
    print(type(my_string))
    # my_store = Store.KNPSStore(None)
    #
    # print(my_store.GetValue( "3c7b48f3-c7af-4405-a2c1-7450f2e3f47b"))










    # with open('dump.sql', 'w') as f:
    #     for line in con.iterdump():
    #         f.write('%s\n' % line)

    # val4 = kgpl.KGPLWiki("Q100000")
    # with open("pickle",'wb') as out_file:
    #     pickle.dump(val4, out_file)
    # with open("pickle",'rb') as input:
    #     val1 = pickle.load(input)
    #
    # print("before: ", type(val4), val4.val, val4.id, val4.url,
    #       val4.annotations, val4.lineage)
    #
    # print("after: ", type(val1), val1.val, val1.id, val1.url,
    #       val1.annotations, val1.lineage)
