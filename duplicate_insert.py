import pickle
import jsonpickle
import json
import os
import requests
import time
import kgpl

import sqlalchemy
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy import distinct

engine = create_engine('sqlite:///KGPLData.db', echo=False)

Session = scoped_session(sessionmaker(bind=engine))
s = Session()

if __name__ == "__main__":
    val1 = kgpl.KGPLStr("val1")
    val2 = kgpl.KGPLStr("val2")
    s.add(val1)
