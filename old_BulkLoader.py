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
    # KGPLVariable = relationship("KGPLVariable", back_populates="wikimap")

    def __init__(self, id, var, modified):
        self.wiki_id = id
        self.var_id = var.id
        self.modified = modified

Base.metadata.create_all(engine)

def load(n):
    start = time.time()
    list_time = []
    with bz2.open('/Users/jack/Downloads/Misc/latest-all.json.bz2', 'rt') as f:
        start = time.time()
        f.read(2)
        count = 0
        for line in f:
            dic = {}
            dic["property"] = {}
            try:
                load_start = time.time()
                entity_obj = json.loads(line[:-2])
                list_time.append(time.time()-load_start)
                count += 1
            except json.decoder.JSONDecodeError:
                print("Error!")
                continue
            dic["entity_id"] = entity_obj["id"]
            dic["modified"] = entity_obj.get("modified")
            fetch = s.query(Wikimap).filter(Wikimap.wiki_id == dic["entity_id"]).one_or_none()
            if fetch:
                if dic["modified"]==fetch.modified:
                    continue
            dic["name"] = entity_obj["labels"].get("en", {}).get("value")
            dic["description"] = entity_obj["descriptions"].get("en", {}).get("value")
            for property_id, snaks in entity_obj['claims'].items():
                dictionary = None
                for snak in snaks:
                    mainsnak = snak.get("mainsnak")
                    qualifiers = snak.get("qualifiers")
                    if mainsnak['snaktype'] != "value":
                        continue
                    datatype = mainsnak["datatype"]
                    datavalue = mainsnak["datavalue"]
                    value_mapping = utils.parse_wikidata_datavalue(datavalue, datatype)
                    if len(value_mapping) == 0:
                        continue
                    qualifiers_mapping = utils.parse_wikidata_qualifiers(qualifiers)
                    assert (set(value_mapping.keys()) != set(qualifiers_mapping.keys()))
                    value_mapping.update(qualifiers_mapping)
                    if dictionary is None:
                        dictionary = value_mapping
                    else:
                        dictionary = dictionary.update(value_mapping)
                if dictionary is None:
                    dic["property"][property_id] = dictionary
                else:
                    dic["property"][property_id] = dictionary
            if fetch:
                    var=kgpl.KGPLVariable(kgpl.KGPLDict(dic))
                    var.id=fetch.var_id
                    s.add(var)
                    fetch.modified=dic["modified"]
            else:
                # todo: wikidata missing
                var=kgpl.KGPLVariable(kgpl.KGPLDict(dic))
                cur_id = 1 + int(
                    s.query(func.count(distinct(kgpl.KGPLVariable.id))).scalar())
                var.id = "V" + str(cur_id)
                s.add(var)
                newdata = Wikimap(dic["entity_id"], var, dic["modified"])
                s.add(newdata)
            if count == n:
                break
    s.commit()






    """
    t1 = time.time()
    for x in range(1, n):
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
    """
