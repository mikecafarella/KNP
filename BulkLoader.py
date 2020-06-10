import pickle
import os
import time
import kgpl
import query
from kgpl.KNPSStore import Session
from kgpl import Base
from kgpl import engine

# ----------
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, \
    PickleType, Float, Table, ForeignKey
from sqlalchemy import func
from sqlalchemy import distinct

s = Session()
# ----------

class Wikimap(Base):
    __tablename__ = 'wikimap'
    wiki_id = Column(UnicodeText, primary_key=True, nullable=False)
    var_id = Column(UnicodeText, ForeignKey('KGPLVariable.id'))
    modified = Column(UnicodeText, nullable=False)
    KGPLVariable = relationship("KGPLVariable", back_populates="wikimap")

    def __init__(self, id, var, modified):
        self.wiki_id = id
        self.var_id = var.id
        self.modified = modified

Base.metadata.create_all(engine)

def load(m, n):
    t1 = time.time()
    for x in range(m, n):
        print(x)
        id = "Q{}".format(x)
        fetch = s.query(Wikimap).filter(Wikimap.wiki_id == id).one_or_none()
        val = kgpl.Wiki_Dict_Transformer(id)
        if fetch:
            if val["modified"] != fetch.modified:
                var = kgpl.KGPLVariable(kgpl.KGPLDict(val))
                var.id = fetch.var_id
                s.add(var)
                fetch.modified = val["modified"]
        else:
            if val["property"]:
                var = kgpl.KGPLVariable(kgpl.KGPLDict(val))
                cur_id = 1 + int(
                    s.query(func.count(distinct(kgpl.KGPLVariable.id))).scalar())
                var.id = "V" + str(cur_id)
                s.add(var)
                newdata = Wikimap(id, var, val["modified"])
                s.add(newdata)
        print("finished")
    s.commit()
    t2 = time.time()
    print("finished all using {}".format(t2-t1))
