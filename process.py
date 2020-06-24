import time
import ujson as json
from multiprocessing import Pool
label_desc = {}

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

infile = open('/data/wikidata/latest-all.json', "rt")
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
                if(line == ']\n'):
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
            label_desc.update(x)
        time2 = time.time()
        total_time = total_time + (time2-time1)
        print(r, time2-time1)
except Exception:
    if len(nn)!=0:
        lst_of_lines.append(nn)
    with Pool(10) as p:
        final = p.map(parse_into_dict, lst_of_lines)

        for x in final:
            label_desc.update(x)
        time2 = time.time()
        total_time = total_time + (time2-time1)
        print(r, time2-time1)

print("Total time", total_time)

time1 = time.time()
print("begin dump")
outfile = open('tt.txt', 'wt')
json.dump(label_desc, outfile)
outfile.close()
print("finish dump", time.time() - time1)

