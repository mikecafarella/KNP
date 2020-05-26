import pickle
import jsonpickle
import json
import os
import requests
import time
import kgpl

class KNPSStore:
  def __init__(self, url):
    self.serverURL = url
    if not os.path.exists("val/"):
        os.mkdir("val/")
    
    if not os.path.exists("var/"):
      os.mkdir("var/")

    if os.path.exists("valueList"):
      infile = open("valueList", "rb")
      self.valueList = pickle.load(infile)
      infile.close()
    else:
      self.valueList = {}

    if os.path.exists("timestamp"):
      infile = open("timestamp", "rb")
      self.varTimestamp = pickle.load(infile)
      infile.close()
    else:
      self.varTimestamp = {}


  def GetValue(self, id: str):
    """Return value given the varName of it. If it can't be found locally and remotely, return None"""
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

  def RegisterVariable(self, value, timestamp):
    """Return variable name and register the new variable on the server"""
    variable = kgpl.KGPLVariable(value)
    r = requests.post(self.serverURL + "/var", json={"variable": jsonpickle.encode(variable)})
    print(r.json())
    filename = r.json()["varName"]
    self.varTimestamp[filename]=timestamp
    self.SaveTimestamp()
    variable.varName = filename
    path = os.path.join("var", filename)
    outfile = open(path, "w")
    outfile.write(jsonpickle.encode(variable))
    outfile.close()
    return filename

  def GetVariable(self, varName: str):
    """Return variable given the varName of it. If it can't be found locally and remotely, return None"""
    # suppose ttl for every variable is 30 sec
    filepath = os.path.join("var", varName)
    if varName in self.varTimestamp:
      if (time.time()-self.varTimestamp[varName])<3:
        # local
        infile = open(filepath, "r")
        var = infile.read()
        print(var)
        infile.close()
        return jsonpickle.decode(var)
      else:
        # remote
        var = self.DownloadVariableFile(varName, time.time())
        return var
    else:
      # remote
      var = self.DownloadVariableFile(varName,time.time())
      return var


  def SetVariable(self, varName, value, timestamp, Config = None):
    """ Here the value is a KGPLclass and in current verion, the value need to be stored ahead to access it later"""
    
    variable = self.GetVariable(varName)
    variable.value = value
    filepath = os.path.join("var", varName)
    outfile = open(filepath, "w");
    outfile.write(jsonpickle.encode(variable))
    outfile.close()
    files = {'file': open(filepath, "rb")}
    r = requests.put(self.serverURL + "/" + filepath, files=files)

  def SaveValueList(self):
    outfile = open("valueList", "wb")
    pickle.dump(self.valueList, outfile)
    outfile.close()
  
  def DownloadVariableFile(self, varName, timestamp):
    filepath = os.path.join("var", varName)
    r = requests.get(self.serverURL + "/var/" + varName)
    if r.status_code == 404:
      print("variable {} not found".format(varName))
      return None
    self.varTimestamp[varName] = timestamp
    self.SaveTimestamp()
    outfile = open(filepath, "wb")
    outfile.write(r.content)
    outfile.close()
    infile = open(filepath, "r")
    data = infile.read()
    print(data)
    var = jsonpickle.decode(data)

    infile.close()
    return var
  
  def SaveTimestamp(self):
    outfile = open("timestamp", "wb")
    pickle.dump(self.varTimestamp, outfile)
    outfile.close()
