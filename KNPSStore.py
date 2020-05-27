import pickle
import jsonpickle
import json
import os
import requests
import time
import kgpl


class KNPSStore:
    """self.serverURL stores the IP address of parent"""

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
            infile = open(file_path, "r")
            val = jsonpickle.decode(infile.read())
            infile.close()
            return val
        elif not self.serverURL:
            return None
        else:
            r = requests.get(os.path.join(self.serverURL, "val", id))
            if r.status_code == 404:
                print("value {} not found".format(id))
                return None
            self.valueList[id] = True
            self.SaveValueList()
            outfile = open(file_path, "w")
            outfile.write(r.json()["value"])
            outfile.close()
            val = jsonpickle.decode(r.json()["value"])
            return val

    def StoreValues(self, inputList):
        """inputList is a list of kgplValue"""
        for value in inputList:
            filename = str(value.id)
            print("storing:" + filename)
            self.valueList[filename] = False
            self.SaveValueList()
            if not os.path.exists(os.path.join("val", filename)):
                outfile = open(os.path.join("val", filename), "w")
                outfile.write(jsonpickle.encode(value))
                outfile.close()

    def PushValues(self):
        if self.serverURL is not None:
            for id in self.valueList:
                if not self.valueList[id]:
                    path = os.path.join("val", id)
                    infile = open(path,"r")
                    val=infile.read()
                    infile.close()
                    self.valueList[id] = True
                    print(self.serverURL + "/val/" + id)
                    r = requests.post(self.serverURL + "/val/" + id, json = {"value": val})
            self.SaveValueList()

    def RegisterVariable(self, value, timestamp):
        """Return variable name and register the new variable on the server"""
        if self.serverURL is not None:
            r = requests.post(self.serverURL + "/var", json={"value": jsonpickle.encode(value), "timestamp": timestamp})
            print(r.json())
            filename = r.json()["varName"]
            var = r.json()["var"]
            self.varTimestamp[filename] = timestamp
            self.SaveTimestamp()
            path = os.path.join("var", filename)
            outfile = open(path, "w")
            outfile.write(var)
            outfile.close()
            return filename
        else:
            variable = kgpl.KGPLVariable(value)
            variable.historical_vals[0][0] = timestamp
            list = os.listdir("var/")
            filename = "K" + len(list)
            path = os.path.join("var", filename)
            outfile = open(path, "w")
            outfile.write(jsonpickle.encode(variable))
            outfile.close()
            return filename


    def GetVariable(self, varName: str):
        """Return variable given the varName of it. If it can't be found locally and remotely, return None"""
        # suppose ttl for every variable is 30 sec
        filepath = os.path.join("var", varName)
        if not self.serverURL:
            try:
                infile = open(filepath, "r")
                var = infile.read()
                print(var)
                infile.close()
                return jsonpickle.decode(var)
            except FileNotFoundError:
                return None
        if varName in self.varTimestamp:
            if (time.time() - self.varTimestamp[varName]) < 3:
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
            var = self.DownloadVariableFile(varName, time.time())
            return var

    def SetVariable(self, varName, value, timestamp, Config=None):
        """ Here the value is a KGPLclass and in current version,
        the value need to be stored ahead to access it later"""

        """variable = self.GetVariable(varName)
        variable.value = value
        filepath = os.path.join("var", varName)
        outfile = open(filepath, "w");
        outfile.write(jsonpickle.encode(variable))
        outfile.close()
        files = {'file': open(filepath, "rb")}
        r = requests.put(self.serverURL + "/" + filepath, files=files)"""
        if not self.serverURL:
            var = self.GetVariable(varName)
            if not var:
                return None
            else:
                var.value = value
                var.historical_vals.append((timestamp, value))
                return var
        filepath = os.path.join("var", varName)
        r = requests.put(self.serverURL + "/" + filepath, json = {"value": jsonpickle.encode(value), "timestamp": timestamp})
        outfile = open(file_path, "w")
        outfile.write(r.json()["var"])
        outfile.close()
        self.varTimestamp[varName] = timestamp
        return jsonpickle.decode(r.json()["var"])

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
        outfile = open(filepath, "w")
        outfile.write(r.json()["var"])
        outfile.close()
        var = jsonpickle.decode(r.json()["var"])
        return var

    def SaveTimestamp(self):
        outfile = open("timestamp", "wb")
        pickle.dump(self.varTimestamp, outfile)
        outfile.close()
