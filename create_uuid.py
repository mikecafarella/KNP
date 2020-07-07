import time
import ujson as json
import uuid
import sqlite3


def main():
    conn = sqlite3.connect("kg.db")
    c = conn.cursor()
    infile = open('/data/wikidata/latest-all.json', "rt")
    start = time.time()
    nn = infile.read(2)
    outfile = open('idDict',"wt")
    outfile.write("{\n")
    try:
        while True:
            ls = []
            for _ in range(0,40000):
                line = infile.readline()
                if line == ']\n':
                    raise Exception('end of line')
                if x[-2] == ',':
                    obj = json.loads(line[:-2])
                else:
                    obj = json.loads(line[:-1])
                id = str(uuid.uuid4())
                ls.append(obj["id"],id)
                outfile.write('\"'+obj["id"]+'\":\"'+id+'\",\n')
            c.executemany("INSERT INTO Wikimap VALUES (?,?)",ls)
    except Exception:
        if len(ls) != 0:
            c.executemany("INSERT INTO Wikimap VALUES (?,?)",ls)
    infile.close()
    outfile.write("}\n")
    outfile.close()
    

if __name__ == "__main__":
    main()
