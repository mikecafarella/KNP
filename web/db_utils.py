import sqlite3
from flask import Flask, g
from web import app
import os
import json
import io


DATABASE = 'web/databases/database.db'
SCHEMA = 'databases/schema.sql'


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
    # print("Stored blob data into: ", filename, "\n")


def insert_results(user_code, action, KG_params, IDs, method, refinements, parameter_transformers, mapping, evaluation_results, user_facing_result):
    
    db = get_db()

    INSERT_RESULT_QUERY = "INSERT INTO results (kpid, method, mapping, {}, rank, type) VALUES(?, ?, ?, ?, ?, ?)"
    INSERT_KP_QUERY = "INSERT INTO knowledge_programs (user_code, KG, KNP_version, KG_params, action) VALUES (?, ?, ?, ?, ?)"
    kpid = db.execute(INSERT_KP_QUERY, (user_code, "WIKIDATA", "KNP_v0", json.dumps(KG_params), action)).lastrowid

    # TODO multiple results
    if method.output_type == "image":
        buf = io.BytesIO()
        user_facing_result.savefig(buf, format='png')
        buf.seek(0)
        blob = buf.read()
        buf.close()
        rid = db.execute(INSERT_RESULT_QUERY.format('result_img'), (kpid, str(method), json.dumps(mapping), blob, 0, "image")).lastrowid
    else:
        raise ValueError("not implemented!")

    # insert evaluation_results
    for refinement, constraints_result in evaluation_results.items():
        for consraint, result in constraints_result.items():
            db.execute("INSERT INTO constraint_evaluation_results (constraint_name, refinement_name, rid, true_false) VALUES (?, ?, ?, ?)", (consraint, refinement, rid, result))

    db.commit()
    return kpid
