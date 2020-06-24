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

    def __init__(self, url, surl="localhost"):
        self.selfurl = surl
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
        self.empty_bulk_list()
        try:
            fetch = s.query(kgpl.KGPLValue).filter(
                kgpl.KGPLValue.id == id).one_or_none()
            if fetch:
                if isinstance(fetch, kgpl.KGPLDict):
                    for key, value in fetch.val.items():
                        self.GetValue(value)
                elif isinstance(fetch, kgpl.KGPLList):
                    for oneitem in fetch.val:
                        self.GetValue(oneitem)
                elif isinstance(fetch, kgpl.KGPLTuple):
                    for onetuple in fetch.val:
                        self.GetValue(onetuple)
                return fetch
            if not self.serverURL:
                return None
            r = requests.get(os.path.join(self.serverURL, "val", id))
            if r.status_code == 404:
                print("value {} not found".format(id))
                return None
            self.valueList[id] = True
            self.SaveValueList()
            got_value = pickle.loads(r.content)
            session.make_transient(got_value)
            got_value.bulkStore()
            # Return value here is abandoned
            if isinstance(got_value, kgpl.KGPLDict):
                for key, value in got_value.val.items():
                    self.GetValue(value)
            elif isinstance(got_value, kgpl.KGPLList):
                for oneitem in got_value.val:
                    self.GetValue(oneitem)
            elif isinstance(got_value, kgpl.KGPLTuple):
                for onetuple in got_value.val:
                    self.GetValue(onetuple)
            return got_value
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print("multiple KGPLValues with the same ID found")
            exit(1)

    def StoreValues(self, inputList):
        """inputList is a list of kgplValue"""
        for value in inputList:
            # print(value)
            if value.id not in self.valueList:
                s.add(value)
                self.valueList[value.id] = False
                self.SaveValueList()
        s.commit()
        # print(value)

    def bulk(self, val):  # need to "emtpy the list for the last time"
        print(len(self.bulkval))
        if len(self.bulkval) > 1:  # can change, I just hard code it.
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
        if self.bulkval:
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

    def PushValue(self, val_id):
        print("-------------pushing value------------")
        self.empty_bulk_list()
        try:
            if self.serverURL is not None:
                # for id in self.valueList:
                #     print(id)
                #     print(self.valueList)
                if val_id not in self.valueList or not self.valueList[
                    val_id]:  # has not been pushed yet
                    fetch = s.query(kgpl.KGPLValue).filter(
                        kgpl.KGPLValue.id == val_id).one_or_none()
                    if not fetch:  # fetch from local database
                        print("value not found in db but should be found")
                        return
                    fetch.url = self.serverURL + "/allvalues/" + fetch.id
                    new = pickle.dumps(fetch)
                    s.commit()

                    self.valueList[val_id] = True
                    self.SaveValueList()
                    # print(self.serverURL + "/val/" + id)
                    r = requests.post(self.serverURL + "/val/" + val_id,
                                      data=new)
                    # session.make_transient(fetch)
                    if isinstance(fetch, kgpl.KGPLDict):
                        print(
                            "------------------is dict!-------------------------")
                        print(fetch)
                        for key, value in fetch.val.items():
                            print(value)
                            self.PushValue(value)
                    elif isinstance(fetch, kgpl.KGPLList):
                        for oneitem in fetch.val:
                            self.PushValue(oneitem)
                    elif isinstance(fetch, kgpl.KGPLTuple):
                        for onetuple in fetch.val:
                            self.PushValue(onetuple)


        except sqlalchemy.orm.exc.MultipleResultsFound:
            print("multiple KGPLValues with the same ID found")
            exit(1)

    def RegisterVariable(self, var):
        self.empty_bulk_list()
        print("-------------store - registering - variable----------------")
        if not self.serverURL:
            # This is the ultimate centralized server.
            # Store into the database here.
            cur_id = 1 + int(
                s.query(func.count(distinct(kgpl.KGPLVariable.id))).scalar())
            var.id = "V" + str(cur_id)
            var.url = self.selfurl + "/allvars/" + var.id
            s.add(var)
            s.commit()
        else:
            # post to the parent server.
            print("-------------------posting to server----------------------")
            r = requests.post(self.serverURL + "/var", data=pickle.dumps(var))
            print(r.json())
            var.id = r.json()["var_id"]
            # assume there is only one layer of server
            var.url = self.serverURL + "/allvars/" + var.id
            self.PushValue(var.currentvalue)
            # val = s.query(kgpl.KGPLValue).filter(
            #     kgpl.KGPLValue.id == var.currentvalue).one_or_none()
            # print("-------------val in db: ", val, "--------------------")
            # requests.post(self.serverURL + "/val/" + var.currentvalue,
            #               data=pickle.dumps(val))

    def GetVariable(self, varName: str):  # varName is V1, V2 ...
        """
        Return variable given the varName of it.
        Always fetch from remote!
        """
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
            # store the value related to the variable to the local database
            self.GetValue(var.currentvalue)
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
            print("---inside------", new_var.timestamp)
            s.add(new_var)
            s.commit()
        else:
            set_var = pickle.dumps(new_var)
            r = requests.post(self.serverURL + "/var/" + new_var.id,
                              data=set_var)
            self.PushValue(new_var.currentvalue)

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
