import time
import ujson as json
from multiprocessing import Pool
#label_desc = {}

def parse_into_dict(lst):
    rst = {}
    for x in lst:
        obj = json.loads(x[:-2])
        curr = []
        curr.append(obj["labels"].get("en", {}).get("value"))
        curr.append(obj["descriptions"].get("en", {}).get("value"))
        rst[obj["id"]] = curr
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
        curr = []
        curr.append(obj["labels"].get("en", {}).get("value"))
        curr.append(obj["descriptions"].get("en", {}).get("value"))
        rst[obj["id"]] = curr
    #print(rst)
    return rst

infile = open('/data/wikidata/latest-all.json', "rt")
outfile = open('tttt.txt',"wt")
outfile.write("{\n")
total_time = 0
nn = infile.read(2)
try:
    for r in range(0, 2500):
        nn = []
        count = 0
        time1=time.time()
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
            for key in x:
                value = x[key]
                outfile.write('\"'+key+'\":['+json.dumps(value[0])+','+json.dumps(value[1])+'],\n')
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
                        outfile.write('\"'+key+'\":['+json.dumps(value[0])+','+json.dumps(value[1])+']\n')
                    else:
                        outfile.write('\"'+key+'\":['+json.dumps(value[0])+','+json.dumps(value[1])+'],\n')
            else:
                for key in x:
                    value = x[key]
                    outfile.write('\"'+key+'\":['+json.dumps(value[0])+','+json.dumps(value[1])+'],\n')
        outfile.write("}\n")
        outfile.close()
        time2 = time.time()
        total_time = total_time + (time2-time1)
        print(r, time2-time1)

print("Total time", total_time)
"""
time1 = time.time()
print("begin dump")
outfile = open('tt.txt', 'wt')
json.dump(label_desc, outfile)
outfile.close()
print("finish dump", time.time() - time1)
"""

