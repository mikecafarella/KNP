import pickle

from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import kgpl
from random import choice

# from string import letters

# engine = create_engine('sqlite:///KGPLData.db', echo=True)
engine = create_engine('sqlite:///KGPLData.db', echo=False)
# engineB = create_engine('sqlite:///KGPLData_reinsert.db', echo=False)

Session = sessionmaker(bind=engine)
s = Session()
#
# Session = sessionmaker(bind=engineB)
# sB = Session()

if __name__ == '__main__':  # If run twice, it will insert twice.

    # create instances of my user object
    val1 = kgpl.KGPLInt(42)
    # print(val1)
    # print(type(val1))
    s.add(val1)
    # s.commit()

    val2 = kgpl.KGPLFloat(42.0)
    s.add(val2)
    # s.commit()
    #
    val3 = kgpl.KGPLStr("42.0 is THE ANSWER!")
    s.add(val3)
    # # s.commit()
    #
    val4 = kgpl.KGPLList([42, "answer"])

    s.add(val4)
    # # s.commit()
    #
    val5 = kgpl.KGPLDict({"test key": "test val"})
    s.add(val5)
    # # s.commit()
    #
    val6 = kgpl.KGPLTuple(("t1", "t2"))
    s.add(val6)
    s.commit()

    # val7 = kgpl.KGPLWiki("Q100000")
    # s.add(val7)
    # s.commit()
    #
    # print("--------val7: wiki---------")
    # for element in s.query(kgpl.KGPLWiki):
    #     print("Database: ", type(element), element.val, element.id,
    #           element.url, element.annotations, element.lineage, element.IR,
    #           element.entity_id, element.description, element.name,
    #           element.properties)
    # print("Directly: ", type(val7), val7.val, val7.id, val7.url,
    #       val7.annotations, val7.lineage, val7.IR, val7.entity_id,
    #       val7.description, val7.name, val7.properties)
    #
    print("--------val6: tuple---------")
    for element in s.query(kgpl.KGPLTuple):
        print("Database: ", type(element), element.val, element.id,
              element.url, element.annotations, element.lineage)
    print("Directly: ", type(val6), val6.val, val6.id, val6.url,
          val6.annotations, val6.lineage)

    print("--------val5: dict---------")
    for element in s.query(kgpl.KGPLDict):
        print("Database: ", type(element), element.val, element.id,
              element.url, element.annotations, element.lineage)
    print("Directly: ", type(val5), val5.val, val5.id, val5.url,
          val5.annotations, val5.lineage)

    print("--------val4: list---------")
    for element in s.query(kgpl.KGPLList):
        print("Database: ", type(element), element.val, element.id,
              element.url,
              element.annotations, element.lineage)
    print("Directly: ", type(val4), val4.val, val4.id, val4.url,
          val4.annotations, val4.lineage)

    print("--------val3: string---------")
    for element in s.query(kgpl.KGPLStr):
        print("Database: ", type(element), element.val, element.id,
              element.url,
              element.annotations, element.lineage)
    print("Directly: ", type(val3), val3.val, val3.id, val3.url,
          val3.annotations, val3.lineage)

    print("--------val2: float---------")
    for element in s.query(kgpl.KGPLFloat):
        print("Database: ", type(element), element.val, element.id,
              element.url,
              element.annotations, element.lineage)
    print("Directly: ", type(val2), val2.val, val2.id, val2.url,
          val2.annotations,
          val2.lineage)

    print("--------val1: int---------")
    for element in s.query(kgpl.KGPLInt):
        print("Database: ", type(element), element.val, element.id,
              element.url, element.annotations, element.lineage)
        # with open("database.out", 'wb') as db:
        #     pickle.dump(element, db)
        # sB.add(element)
        # sB.commit()

    print("Directly: ", type(val1), val1.val, val1.id, val1.url,
          val1.annotations, val1.lineage)
    #
    # with open("direct.out", 'wb') as direct:
    #     pickle.dump(val1, direct)

    # IR = Column(PickleType, nullable=True)
    # entity_id = Column(Unicode)
    # description = Column(Unicode, nullable=True)
    # name = Column(Unicode,nullable=True)
    # properties = Column(PickleType,nullable=True)

    # u = User('nosklo')
    # u.address = '66 Some Street #500'
    #
    # u2 = User('lakshmipathi')
    # u2.password = 'ihtapimhskal'
    #
    # # testing
    # s.add_all([u, u2])
    # s.commit()
