import pickle
import os
import time
import kgpl
import query
from KNPSStore import Session

# ----------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///KGPLData.db', echo=False)
Base = declarative_base(bind=engine)
# ----------




def load(n):
    t1 = time.time()
    if os.path.exists("bulkList"):
        infile = open("bulkList", "rb")
        bulkList = pickle.load(infile)
        infile.close()
    else:
        bulkList = {}
    s = Session()
    for x in range(1, n):
        print(x)
        id = "Q{}".format(x)
        if id in bulkList:
            fetch = s.query(kgpl.KGPLValue).filter_by(kgpl.KGPLValue.id == bulkList[id]).first()
            fetch.val = kgpl.Wiki_Dict_Transformer(id)
        else:
            tempDict = kgpl.Wiki_Dict_Transformer(id)
            if tempDict:
                piece = kgpl.KGPLDict(tempDict)
                bulkList[id] = piece.id
                s.add(piece)
        print("finished")
    s.commit()
    outfile = open("bulkList", "wb")
    pickle.dump(bulkList, outfile)
    outfile.close()
    t2 = time.time()
    print("finished all using {}".format(t2-t1))

