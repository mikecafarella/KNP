import time
import ujson as json
import uuid
from multiprocessing import Pool
import sqlite3
#label_desc = {}

def parse_into_dict(lst):
    rst = {}
    for x in lst:
        obj = json.loads(x[:-2])
        rst[obj["id"]] = str(uuid.uuid4())    
        #print(rst)
    return rst

def parse_into_dict_end_file(lst):
    rst = {}
    for x in lst:
        if x[-2] == ',':
            obj = json.loads(x[:-2])
        else:
            print("last line without comma")
            obj = json.loads(x[:-1])
        rst[obj["id"]] = str(uuid.uuid4())
    #print(rst)
    return rst

def main():
    conn = sqlite3.connect("kg.db")
    c = conn.cursor()
    infile = open('/data/wikidata/latest-all.json', "rt")
    outfile = open('idDict',"wt")
    outfile.write("{\n")
    total_time = 0
    nn = infile.read(2)
    try:
        for r in range(0, 2500):
            nn = []
            count = 0
            time1 = time.time()
            lst_of_lines = []
            for i in range(0, 10):
                while True:
                    line = infile.readline()
                    if line == ']\n':
                        raise Exception('end of line')
                    nn.append(line)
                    count = count + 1
                    if count == 4000:
                        lst_of_lines.append(nn)
                        nn = []
                        count = 0
                        break

            with Pool(10) as p:
                final = p.map(parse_into_dict, lst_of_lines)

            for x in final:
                for key,value in x.items():
                    outfile.write('\"'+key+'\":\"'+value+'\",\n')
                    c.execute("INSERT INTO Wikimap VALUES (?,?)",(key,value,))
            conn.commit()
            time2 = time.time()
            total_time = total_time + (time2-time1)
            print(r, time2-time1)
    except Exception:
        if len(nn)!=0:
            lst_of_lines.append(nn)
        with Pool(10) as p:
            final = p.map(parse_into_dict_end_file, lst_of_lines)
            for idx,x in enumerate(final):
                if idx == len(final)-1:
                    list_of_key = list(x.keys())
                    sz = len(list_of_key)
                    for i,key in enumerate(list_of_key):
                        value = x[key]
                        if i == sz - 1:
                            outfile.write('\"'+key+'\":\"'+value+'\"\n')
                        else:
                            outfile.write('\"'+key+'\":\"'+value+'\",\n')
                        c.execute("INSERT INTO Wikimap VALUES (?,?)",(key,value,))
                else:
                    for key,value in x.items():
                        outfile.write('\"'+key+'\":\"'+value+'\",\n')
                        c.execute("INSERT INTO Wikimap VALUES (?,?)",(key,value,))
            conn.commit()
            outfile.write("}\n")
            outfile.close()
            time2 = time.time()
            total_time = total_time + (time2-time1)
            print(r, time2-time1)

    print("Total time", total_time)

if __name__ == "__main__":
    main()
