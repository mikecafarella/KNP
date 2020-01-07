import sqlite3
from flask import Flask, g
from web import app
import os


DATABASE = 'web/databases/database.db'
SCHEMA = 'databases/schema.sql'

INSERT_RESULT_QUERY = "INSERT INTO results (kpid, method, KG, KNP_version, {}, rank) VALUES(?, ?, ?, ?, ?, ?)"
INSERT_KP_QUERY = "INSERT INTO knowledge_programs (program) VALUES (?)"




def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def insert(query, args):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def drop_db():
    with app.app_context():
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
        setattr(g, '_database', None)
    os.remove(DATABASE)


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")