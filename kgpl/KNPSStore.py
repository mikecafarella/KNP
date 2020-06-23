import pickle
import jsonpickle
import json
import os
import requests
import time
import kgpl
import sqlite3


import sqlalchemy
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy import distinct

engine = create_engine('sqlite:///KGPLData.db', echo=False,
                       connect_args={'check_same_thread': False})

Session = scoped_session(sessionmaker(bind=engine))
s = Session()
s.expire_on_commit = False
conn = sqlite3.connect("KGPLData.db")
c = conn.cursor()

class KNPSStore:
    """self.serverURL stores the IP address of parent"""

    def __init__(self, url):
        self.serverURL = url
        self.bulkval = []
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
        try:
            fetch = s.query(kgpl.KGPLValue).filter(
                kgpl.KGPLValue.id == id).one_or_none()
            if fetch:
                return fetch
            if not self.serverURL:
                return None
            r = requests.get(os.path.join(self.serverURL, "val", id))
            if r.status_code == 404:
                print("value {} not found".format(id))
                return None
            self.valueList[id] = True
            self.SaveValueList()
            val = pickle.loads(r.content)
            session.make_transient(val)
            s.add(val)
            s.commit()
            return val
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print("multiple KGPLValues with the same ID found")
            exit(1)

    def StoreValues(self, inputList):
        """inputList is a list of kgplValue"""

        for value in inputList:
            # print(value)
            if value.id not in self.valueList:
                s.add(value)
                # TODO: move out
                self.valueList[value.id] = False
                self.SaveValueList()
        s.commit()
        # print(value)

    def bulk(self, val): # need to "emtpy the list for the last time"
        print(len(self.bulkval))
        if len(self.bulkval) > 1: # can change, I just hard code it.
            print("lenth>1")
            self.bulkval.append(val)
            for one_bulk in self.bulkval:
                try:
                    c.execute(
                        "INSERT INTO KGPLValue VALUES (?,?,?,?,?,?,?)",
                        (one_bulk.id, pickle.dumps(one_bulk.val),
                         pickle.dumps(one_bulk.lineage),
                         one_bulk.url, one_bulk.annotations,
                         type(one_bulk).__name__, None)
                    )
                except sqlite3.IntegrityError:
                    print("duplicate insertion: Skipping...")
            conn.commit()
            self.bulkval = []
        else:
            self.bulkval.append(val)

    def empty_bulk_list(self):
        for one_bulk in self.bulkval:
            c.execute(
                "INSERT INTO KGPLValue VALUES (?,?,?,?,?,?,?)",
                (one_bulk.id, pickle.dumps(one_bulk.val),
                 pickle.dumps(one_bulk.lineage),
                 one_bulk.url, one_bulk.annotations,
                 type(one_bulk).__name__, None)
            )
        conn.commit()
        self.bulkval = []

    def PushValues(self):
        print("-------------pushing value------------")
        try:
            if self.serverURL is not None:
                for id in self.valueList:
                    print(id)
                    print(self.valueList)
                    if not self.valueList[id]:  # fetch from local database
                        fetch = s.query(kgpl.KGPLValue).filter(
                            kgpl.KGPLValue.id == id).one_or_none()
                        if not fetch:
                            print("value not found in db but should be found")
                            return
                        new = pickle.dumps(fetch)
                        self.valueList[id] = True
                        print(self.serverURL + "/val/" + id)
                        r = requests.post(self.serverURL + "/val/" + id,
                                          data=new)
                self.SaveValueList()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print("multiple KGPLValues with the same ID found")
            exit(1)

    def RegisterVariable(self, var):
        print(
            "----------------store - registering - variable-------------------")
        if not self.serverURL:
            # This is the ultimate centralized server.
            # Store into the database here.
            cur_id = 1 + int(
                s.query(func.count(distinct(kgpl.KGPLVariable.id))).scalar())
            var.id = "V" + str(cur_id)
            var.url = "we_have_not_implement_sharing_service_yet"
            s.add(var)
            s.commit()
        else:
            # post to the parent server.
            print("-------------------posting to server----------------------")
            r = requests.post(self.serverURL + "/var", data=pickle.dumps(var))
            print(r.json())
            var.id = r.json()["var_id"]
            var.url = "not_implement_sharing_service_yet"

            val = s.query(kgpl.KGPLValue).filter(
                kgpl.KGPLValue.id == var.currentvalue).one_or_none()
            print("-------------val in db: ", val, "--------------------")
            requests.post(self.serverURL + "/val/" + var.currentvalue,
                          data=pickle.dumps(val))

    def GetVariable(self, varName: str):  # varName is V1, V2 ...
        """
        Return variable given the varName of it.
        Always fetch from remote!
        """
        # TODO: Currently we have redundant field "history val" in the database
        if not self.serverURL:
            try:
                fetch = s.query(kgpl.KGPLVariable).filter(
                    kgpl.KGPLVariable.id == varName).order_by(
                    kgpl.KGPLVariable.timestamp.desc()).first()

                his = s.query(kgpl.KGPLVariable).filter(
                    kgpl.KGPLVariable.id == varName).order_by(
                    kgpl.KGPLVariable.timestamp.desc())
                fetch.historical_vals = []
                for one_his in his:
                    fetch.historical_vals.append(
                        (one_his.timestamp, one_his.currentvalue))

                print("historical values: ", fetch.historical_vals)
                session.make_transient(fetch)
                return fetch
            except sqlalchemy.orm.exc.NoResultFound:
                # return sth showing no related result
                print("-------------variable not found------------")
                return None
        else:
            r = requests.get(os.path.join(self.serverURL, "var", varName))
            var = pickle.loads(r.content)
            # session.make_transient(var)
            return var
            # fetch from remote

    def availVar(self):
        if not self.serverURL:
            try:
                num = s.query(kgpl.KGPLVariable.id).distinct().count()
                return int(num)
            except sqlalchemy.orm.exc.NoResultFound:
                print("-------------variable not found------------")
                return -1
        else:
            return -1

    def availVal(self):
        if not self.serverURL:
            try:
                fetch = s.query(kgpl.KGPLValue)
                rst = []
                for one_fetch in fetch:
                    # session.make_transient(one_fetch)
                    rst.append((one_fetch.id, one_fetch.val,
                                type(one_fetch).__name__))
                return rst
            except sqlalchemy.orm.exc.NoResultFound:
                print("-------------variable not found------------")
                return -1
        else:
            return -1

    def SetVariable(self, new_var):  # new_var is the new variable
        print("------------------setting variable--------------------")
        """
        Reset the value of a variable,
        Update in the database(add a line)
        """

        if not self.serverURL:
            # self.StoreValues([new_var, ])
            print("---inside------", new_var.timestamp)

            s.add(new_var)
            s.commit()
        else:
            set_var = pickle.dumps(new_var)
            r = requests.post(self.serverURL + "/var/" + new_var.id,
                              data=set_var)

            val = s.query(kgpl.KGPLValue).filter(
                kgpl.KGPLValue.id == new_var.currentvalue).one_or_none()
            print("-------------val in db: ", val, "--------------------")
            requests.post(self.serverURL + "/val/" + new_var.currentvalue,
                          data=pickle.dumps(val))

    def SaveValueList(self):
        outfile = open("valueList", "wb")
        pickle.dump(self.valueList, outfile)
        outfile.close()

    def DownloadVariableFile(self, varName, timestamp):
        filepath = os.path.join("../var", varName)
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

    # def GetVariable(self, varName: str):
    #     """Return variable given the varName of it. If it can't be found locally and remotely, return None"""
    #     # suppose ttl for every variable is 30 sec
    #     filepath = os.path.join("var", varName)
    #     if not self.serverURL:
    #         try:
    #             infile = open(filepath, "r")
    #             var = infile.read()
    #             print(var)
    #             infile.close()
    #             return jsonpickle.decode(var)
    #         except FileNotFoundError:
    #             return None
    #     if varName in self.varTimestamp:
    #         if (time.time() - self.varTimestamp[varName]) < 3:
    #             # local
    #             infile = open(filepath, "r")
    #             var = infile.read()
    #             print(var)
    #             infile.close()
    #             return jsonpickle.decode(var)
    #         else:
    #             # remote
    #             var = self.DownloadVariableFile(varName, time.time())
    #             return var
    #     else:
    #         # remote
    #         var = self.DownloadVariableFile(varName, time.time())
    #         return var

    # def RegisterVariable(self, value, timestamp):
    #     """Return variable name and register the new variable on the server"""
    #     if self.serverURL is not None:
    #         r = requests.post(self.serverURL + "/var",
    #                           json={"value": jsonpickle.encode(value),
    #                                 "timestamp": timestamp})
    #         print(r.json())
    #         filename = r.json()["varName"]
    #         var = r.json()["var"]
    #         self.varTimestamp[filename] = timestamp
    #         self.SaveTimestamp()
    #         path = os.path.join("var", filename)
    #         outfile = open(path, "w")
    #         outfile.write(var)
    #         outfile.close()
    #         return filename
    #     else:
    #         variable = kgpl.KGPLVariable(value)
    #         variable.historical_vals[0] = (
    #             timestamp, variable.historical_vals[0][1])
    #         print(variable.historical_vals)
    #         list = os.listdir("var/")
    #         filename = "K" + str(len(list))
    #         variable.varName = filename
    #         path = os.path.join("var", filename)
    #         outfile = open(path, "w")
    #         outfile.write(jsonpickle.encode(variable))
    #         outfile.close()
    #         return filename

    # def SetVariable(self, varName, value, timestamp, Config=None):
    #     """ Here the value is a KGPLclass and in current version,
    #     the value need to be stored ahead to access it later"""
    #
    #     """variable = self.GetVariable(varName)
    #     variable.value = value
    #     filepath = os.path.join("var", varName)
    #     outfile = open(filepath, "w");
    #     outfile.write(jsonpickle.encode(variable))
    #     outfile.close()
    #     files = {'file': open(filepath, "rb")}
    #     r = requests.put(self.serverURL + "/" + filepath, files=files)"""
    #     if not self.serverURL:
    #         var = self.GetVariable(varName)
    #         if not var:
    #             return None
    #         else:
    #             var.currentvalue = value
    #             var.historical_vals.append((timestamp, value))
    #             filepath = os.path.join("var", varName)
    #             outfile = open(filepath, "w")
    #             outfile.write(jsonpickle.encode(var))
    #             outfile.close()
    #             return var
    #     filepath = os.path.join("var", varName)
    #     print(filepath)
    #     r = requests.put(self.serverURL + "/" + filepath,
    #                      json={"value": jsonpickle.encode(value),
    #                            "timestamp": timestamp})
    #     outfile = open(filepath, "w")
    #     outfile.write(r.json()["var"])
    #     outfile.close()
    #     self.varTimestamp[varName] = timestamp
    #     return jsonpickle.decode(r.json()["var"])
