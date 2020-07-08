import wiki_utils
import os
import time
import pickle
import kgpl
from multiprocessing import Pool
from multiprocessing import Process
import ujson as json
import sqlite3
import csv

def generate_dict(lst, d):
    # print(os.getpid(),"started!")
    lst_of_dict = []
    for line in lst:
        datalst = []
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
                value_mapping = wiki_utils.parse_wikidata_datavalue(datavalue, datatype)
                if len(value_mapping) == 0:
                    continue
                qualifiers_mapping = wiki_utils.parse_wikidata_qualifiers(qualifiers)
                # assert (set(value_mapping.keys()) != set(qualifiers_mapping.keys()))
                value_mapping.update(qualifiers_mapping)
                if dictionary is None:
                    dictionary = value_mapping
                else:
                    dictionary = dictionary.update(value_mapping)
            if dictionary is None:
                dic["property"][property_id] = dictionary
            else:
                dic["property"][property_id] = dictionary
        kgpl.KGPLDict(dic, None, datalst, wiki_utils.iddict[entity_obj["id"]])
        lst_of_dict.append(datalst)
    #print(rst)
    #print(os.getpid(),"writing")
    filename = d+"/"+str(os.getpid())+".csv"
    outfile = open(filename, "w", newline='')
    """
    for x in lst_of_dict:
        for xx in x:
            to_write = [xx.id + '\n', 
                        json.dumps(xx.val) + '\n',
                        xx.url + '\n',
                        xx.annotations + '\n',
                        type(xx).__name__ + '\n'
                        ]
            outfile.writelines(to_write)
    """
    writer = csv.writer(outfile)
    for x in lst_of_dict:
        for xx in x:
            writer.writerow([xx.id,json.dumps(xx.val),pickle.dumps(kgpl.Lineage.InitFromPythonVal()),xx.url,xx.annotations,type(xx).__name__,None])
    outfile.close()
    #print("generating finished")


def generate_dict_dir0(lst):
    generate_dict(lst, "dir0")


def generate_dict_dir1(lst):
    generate_dict(lst, "dir1")


def load_db(d):
    print("loading start")
    conn = sqlite3.connect("ningning.db")
    c = conn.cursor()
    file = os.listdir(d)
    for f in file:
        #echo -e '.separator "," \n.import testing.csv KGPLValue' | sqlite3 ningning.db
        filename = d+"/"+f
        exe = "echo '.separator \",\"\n.mode csv\n.import {} KGPLValue' | sqlite3 ningning.db".format(filename)
        code=os.system(exe)
        if code !=0:
            print("error")
        os.remove(filename)
    print("loading finished")


def generate_dict_end_file(lst):
    print(os.getpid(),"started!")
    lst_of_dict = []
    for x in lst:
        datalst=[]
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
                value_mapping = wiki_utils.parse_wikidata_datavalue(datavalue, datatype)
                if len(value_mapping) == 0:
                    continue
                qualifiers_mapping = wiki_utils.parse_wikidata_qualifiers(qualifiers)
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
        kgpl.KGPLDict(dic, None, datalst,wiki_utils.iddict[entity_obj["id"]])
        lst_of_dict.append(datalst)
    #print(rst)
    print(os.getpid(),"writing")
    filename = d+"/"+str(os.getpid())+".csv"
    outfile = open(filename, "w", newline='')
    writer = csv.writer(outfile)
    for x in lst_of_dict:
        for xx in x:
            writer.writerow([xx.id,json.dumps(xx.val),pickle.dumps(kgpl.Lineage.InitFromPythonVal()),xx.url,xx.annotations,type(xx).__name__,None])
    outfile.close()
    print("finish")


def main():
    total_time = 0
    with open('/data/wikidata/latest-all.json', 'rt') as f:
        f.read(2)
        # round 0
        nn=[]
        count = 0
        time1=time.time()
        lst_of_lines = []
        for i in range(0, 12):
            while True:
                line = f.readline()
                nn.append(line)
                count = count + 1
                if count == 4000:
                    if i!=0 and i!=2:
                        lst_of_lines.append(nn)
                    nn = []
                    count = 0
                    break
        with Pool(10) as p:
            final = p.map(generate_dict_dir0, lst_of_lines, 1)
        time2 = time.time()
        total_time = total_time + (time2-time1)
        print("0", time2-time1)
        # round 0
        try:
            for r in range(1, 5):
                nn=[]
                count = 0
                time1=time.time()
                lst_of_lines = []
                for i in range(0, 10):
                    while True:
                        line = f.readline()
                        if line == ']\n':
                            raise Exception('end of line')
                        nn.append(line)
                        count = count + 1
                        if count == 4000:
                            lst_of_lines.append(nn)
                            nn = []
                            count = 0
                            break
                # insert dir0 into db, pickle dump into dir1
                if r % 2 == 1:
                    p = Process(target=load_db, args=("dir0",))
                    p.start()
                    with Pool(10) as pool:
                        final = pool.map(generate_dict_dir1, lst_of_lines, 1)
                    p.join()
                    #load_db("dir0")
                else:
                    p = Process(target=load_db, args=("dir1",))
                    p.start()
                    with Pool(10) as pool:
                        final = pool.map(generate_dict_dir0, lst_of_lines, 1)
                    p.join()
                    #load_db("dir1")
                
                time2 = time.time()
                total_time = total_time + (time2-time1)
                print(r, time2-time1)
        except Exception:
            if len(nn)!=0:
                lst_of_lines.append(nn)
            with Pool(10) as p:
                final = p.map(generate_dict_end_file, lst_of_lines, 1)
                
                time2 = time.time()
                total_time = total_time + (time2-time1)
                print(r, time2-time1)

if __name__ == '__main__':
    main()
