#!/usr/bin/env python3
import time
import kgpl
from multiprocessing import Pool
import ujson as json
import numpy as np
import bz2
import utils
import sqlite3
import pickle

conn = sqlite3.connect("KGPLData.db")
c = conn.cursor()

def generate_dict(lst):
    lst_of_dict = []
    for line in lst:
        dic = {}
        dic["property"] = {}
        entity_obj = json.loads(line[:-2])
        dic["entity_id"] = entity_obj["id"]
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
        kgpl.KGPLDict(dic, None, lst_of_dict)
    #print(rst)
    return lst_of_dict



def generate_dict_end_file(lst):
    lst_of_dict = []
    for x in lst:
        dic = {}
        dic["property"] = {}
        if x[-2] == ',':
            entity_obj = json.loads(x[:-2])
        else:
            print("last line without comma")
            entity_obj = json.loads(x[:-1])
        dic["entity_id"] = entity_obj["id"]
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
        kgpl.KGPLDict(dic, None, lst_of_dict)
    #print(rst)
    return lst_of_dict



total_time = 0
start = time.time()
with open('/data/wikidata/latest-all.json', 'rt') as f:
    start = time.time()
    f.read(2)
    try:
        for r in range(0, 20):
            print("begin reading")
            nn=[]
            count = 0
            time1=time.time()
            lst_of_lines = []
            for i in range(0, 20):
                while True:
                    line = f.readline()
                    if line == ']\n':
                        raise Exception('end of line')
                    nn.append(line)
                    count = count + 1
                    if count == 50:
                        lst_of_lines.append(nn)
                        nn = []
                        count = 0
                        break
            print("begin map", time.time() - time1)
            with Pool(20) as p:
                final = p.map(generate_dict, lst_of_lines)
            print("begin storing", time.time() - time1)
            for x in final:
                for one_bulk in x:
                    try:
                        c.execute(
                            "INSERT INTO KGPLValue VALUES (?,?,?,?,?,?,?)",
                            (one_bulk.id, pickle.dumps(one_bulk.val),
                            pickle.dumps(one_bulk.lineage),
                            one_bulk.url, one_bulk.annotations,
                            type(one_bulk).__name__, None)
                        )
                    except sqlite3.IntegrityError:
                        print("duplicate insertion: Skipping...")
            conn.commit()
            time2 = time.time()
            total_time = total_time + (time2-time1)
            print(r, time2-time1)
    except Exception:
        if len(nn)!=0:
            lst_of_lines.append(nn)
        with Pool(10) as p:
            final = p.map(generate_dict_end_file, lst_of_lines)
            for x in final:
                for one_bulk in x:
                    try:
                        c.execute(
                            "INSERT INTO KGPLValue VALUES (?,?,?,?,?,?,?)",
                            (one_bulk.id, pickle.dumps(one_bulk.val),
                            pickle.dumps(one_bulk.lineage),
                            one_bulk.url, one_bulk.annotations,
                            type(one_bulk).__name__, None)
                        )
                    except sqlite3.IntegrityError:
                        print("duplicate insertion: Skipping...")
            conn.commit()
            time2 = time.time()
            total_time = total_time + (time2-time1)
            print(r, time2-time1)
