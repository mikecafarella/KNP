import csv
import kgpl
import pickle

def main():
    with open("../9251","r") as fp:
        with open("temp","w") as fw:
            read_id = fp.readline()
            read_id = read_id[:-1]
            read_val = fp.readline()[:-1]
            read_url = fp.readline()[:-1]
            read_annotations = fp.readline()[:-1]
            read_type = fp.readline()[:-1]
            writer = csv.writer(fw)
            p=pickle.dumps(kgpl.Lineage.InitFromPythonVal())
            writer.writerow([read_id, read_val,p,read_url, read_annotations, read_type,None])

if __name__ == "__main__":
    main()
