import pickle
import os
import requests
from datetime import datetime
import kgpl

class KNPSStore:
  def __init__(self):
    self.serverURL = "http://107.191.51.32:5000"
    if not os.path.exists("val/"):
        os.mkdir("val/")
    if os.path.exists("valueList"):
      infile = open("valueList", "rb")
      self.valueList = pickle.load(infile)
      infile.close()
    else:
      self.valueList = {}

  def GetValue(self, id: str):
    file_path = os.path.join("val", id)
    if os.path.exists(file_path):
      # find the value locally
      infile = open(file_path, "rb")
      val = pickle.load(infile)
      infile.close()
      return val
    else:
      r = requests.get(os.path.join(self.serverURL, "val", id))
      if r.status_code == 404:
        print("value {} not found".format(id))
        return None
      self.valueList[id] = True
      self.SaveValueList()
      outfile = open(file_path, "wb")
      outfile.write(r.content)
      outfile.close()
      infile = open(file_path, "rb")
      val = pickle.load(infile)
      return val

  def StoreValues(self, inputList):
    for value in inputList:
      filename = str(value.id)
      print("storing:" + filename)
      self.valueList[filename] = False
      self.SaveValueList()
      if not os.path.exists(os.path.join("val", filename)):
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
    """Return variable given the varName of it. If it can't be found locally and remotely, return None"""
    # suppose ttl for every variable is 30 sec
    filepath = os.path.join("var", varName)
    if varName in self.varTimestamp:
      if (datetime.now()-self.varTimestamp[varName]).seconds<30:
        # local
        infile = open(filepath, "rb")
        variable = pickle.load(infile)
        infile.close()
        return variable
      else:
        # remote
        var = self.DownloadVariableFile(self,varName)
        return var
    else:
      # remote
      var = self.DownloadVariableFile(self,varName)
      return var


  def SetVariable(self, varName, Value, Config = None):
    """ Here the value is a KGPLclass """
    variable = self.GetVariale(varName)
    variable.reassign(Value)
    filepath = os.path.join("var", varName)
    outfile = open(filepath, "wb");
    pickle.dump(variable, outfile)
    outfile.clode()
    files = {'file': open(filepath, "rb")}
    r = requests.post(self.serverURL + "/" + filepath, files=files)

  def SaveValueList(self):
    outfile = open("valueList", "wb")
    pickle.dump(self.valueList, outfile)
    outfile.close()
  
  def DownloadVariableFile(self, varName):
    filepath = os.path.join("var", varName)
    r = requests.get(self.serverURL + "/var/" + varName)
    if r.status_code == 404:
      print("variable {} not found".format(varName))
      return None
    self.varTimestamp[varName] = datetime.now()
    outfile = open(filepath, "wb")
    outfile.write(r.content)
    outfile.close()
    infile = open(filepath, "rb")
    var = pickle.load(infile)
    return var