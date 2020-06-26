infile = open('/data/wikidata/latest-all.json', "rt")
line = infile.readline()
line2 = infile.readline()
while line2:
    line=line2
    line2 = infile.readline()
print(line)
