import pickle
import os
import requests
import json
from datetime import datetime
from kgpl import KGPLValue, KGPLVariable

class KNPSStore:
  def __init__(self):
    self.serverURL = "http://107.191.51.32:5000"
    if os.path.exists("valueList"):
      infile = open("valueList", "rb")
      self.valueList = pickle.load(infile)
      infile.close()
    else:
      self.valueList = {}

  def __del__(self):
    print("destructor called")
    outfile = open("valueList", "wb")
    pickle.dump(self.valueList, outfile)
    outfile.close()
  

  def GetValue(self, id: str):
    file_path = os.path.join("val", id)
    if os.path.exists(file_path):
      # find the value locally
      infile = open(file_path, "rb")
      val = pickle.load(infile)
      infile.close()
      return val
    else:
      self.valueList[id] = True
      self.SaveValueList()
      r = requests.get(os.path.join(self.serverURL, "val", id))
      response = r.json()
      value = r[0]['value']
      outfile = open(id, "wb")
      pickle.dump(value, outfile)
      outfile.close()
      return val

  def StoreValues(self, valueList):
    for value in valueList:
      filename = str(value.id)
      print("store" + filename)
      self.valueList[filename] = False
      self.SaveValueList()
      if not os.path.exists("val/"):
        os.mkdir("val/")
      if not os.path.exists(filename):
        outfile = open(os.path.join("val", filename), "wb")
        pickle.dump(value, outfile)
        outfile.close()

  def PushValues(self):
    for id in self.valueList:
      if not self.valueList[id]:
        path = os.path.join("val", id)
        files = {'file': open(path, "rb")}
        self.valueList[id] = True
        self.SaveValueList()
        print(self.serverURL + "/val/" + id)
        r = requests.post(self.serverURL + "/val/" + id, files=files)
    

  def GetVariale(self, varName: str):
    # suppose ttl for every variable is 30 sec
    if varName in self.varTimestamp:
      if (datetime.now()-self.varTimestamp[varName]).seconds<30:
        # local
        pass
      else:
        # remote
        pass
      varTimestamp[varName] = datetime.now()
    else:
      varTimestamp[varName] = datetime.now()
      # remote


  def SetVariable(self, varName, Value):
    self.varTimestamp[varName] = datetime.now()
    pass

  def SaveValueList(self):
    outfile = open("valueList", "wb")
    pickle.dump(self.valueList, outfile)
    outfile.close()
    