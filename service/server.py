from flask import Flask, abort, request, jsonify, render_template, url_for, redirect
from flask_cors import CORS

from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from sqlalchemy import select

from okta_helpers import is_access_token_valid, is_id_token_valid, config
from okta_user import User as FlaskUser

from models import *
from functions import execute_function, get_dobj_contents
from database import SessionLocal, engine

from markupsafe import escape
from neo4j import GraphDatabase

import base64
import json
import datetime
import asyncio
import time
import os
from pathlib import Path
import requests
import uuid

from elasticsearch import Elasticsearch

# This is just a temporary thing for demos so we can all run off diferent indexes on the elsasticsearch server
machine_id = uuid.UUID(int=uuid.getnode())

ES_INDEX = 'knps-00000000-0000-0000-0000-acde48001122' #'knps-{}'.format(machine_id)
ES_HOST = 'ec2-52-201-28-150.compute-1.amazonaws.com'


GDB = None

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.config.update({'SECRET_KEY': 'SomethingNotEntirelySecret'})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knps.db'
db = SessionLocal()
ma = Marshmallow(app)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

APP_STATE = 'ApplicationStateKNPS'
NONCE = 'SampleNonceKNPS'

NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
NEO4J_PORT = int(os.getenv('NEO4J_PORT', '7687'))
KNPS_SERVER_HOST = os.getenv('KNPS_SERVER_HOST', 'localhost')
KNPS_SERVER_PORT = int(os.getenv('KNPS_SERVER_PORT', '5000'))

loop = asyncio.get_event_loop()


###########################################
# Login/logout helper functions
###########################################
@app.route("/logged_in")
def logged_in():
    return '<h2>Thank you for logging in.</h2>'

@app.route("/cli_login")
def cli_login():
    access_token = request.args.get("access_token", None)

    if access_token and is_access_token_valid(access_token, config["issuer"], config["client_id"]):
        print ("VALID")
        pass
    else:
        login_state = 'cli_{}'.format(uuid.uuid1())

        # get request params
        query_params = {'client_id': config["client_id"],
                        'redirect_uri': f'http://{KNPS_SERVER_HOST}:{KNPS_SERVER_PORT}/authorization-code/callback',
                        'scope': "openid email profile",
                        'state': login_state,
                        'nonce': NONCE,
                        'response_type': 'code',
                        'response_mode': 'query'}

        # build request_uri
        request_uri = "{base_url}?{query_params}".format(
            base_url=config["auth_uri"],
            query_params=requests.compat.urlencode(query_params)
        )
        data = {'login_url': request_uri, 'login_code': login_state}
        return json.dumps(data)

@app.route("/cli_logout", methods=['POST'])
def cli_logout():
    access_token = request.form.get("access_token", None)

    # if access_token and is_access_token_valid(access_token, config["issuer"], config["client_id"]):
    login_state = 'cli_{}'.format(uuid.uuid1())

    # get request params
    query_params = {'id_token_hint': access_token, 'redirect_uri': 'http://localhost'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=config["auth_uri"],
        query_params=requests.compat.urlencode(query_params)
    )
    data = {'logout_url': request_uri}

    return json.dumps(data)

@app.route("/get_token", methods=['POST'])
def get_token():
    login_code = request.form.get("login_code", None)

    if not login_code:
        return "Missing login code", 403

    countdown = 60
    while countdown > 0:
        data_file = 'data/login_info.json'
        p = Path(data_file)
        if p.exists():
            with open(data_file, 'rt') as f:
                data = json.load(f)
        else:
            data = {}

        if login_code in data:
            user_data = json.dumps(data[login_code])

            # Clear out this login_code, since it's not useful anymore
            del(data[login_code])

            if not Path(data_file).exists():
                os.makedirs(os.path.dirname(data_file))
            with open(data_file, 'wt') as f:
                json.dump(data, f, indent=2)

            return user_data

        countdown = countdown - 1
        time.sleep(1)

    return "Timeout", 403

@app.route("/login")
def login():
    # get request params
    query_params = {'client_id': config["client_id"],
                    'redirect_uri': config["redirect_uri"],
                    'scope': "openid email profile",
                    'state': APP_STATE,
                    'nonce': NONCE,
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=config["auth_uri"],
        query_params=requests.compat.urlencode(query_params)
    )

    return redirect(request_uri)

@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    login_state = request.args.get("state")

    if not code:
        return "The code was not returned or is not accessible", 403

    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url
                    }

    print(code)
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        config["token_uri"],
        headers=headers,
        data=query_params,
        auth=(config["client_id"], config["client_secret"]),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    print(access_token)

    if not is_access_token_valid(access_token, config["issuer"], config["client_id"]):
        return "Access token is invalid", 403

    if not is_id_token_valid(id_token, config["issuer"], config["client_id"], NONCE):
        return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(config["userinfo_uri"],
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = "{} {}".format(userinfo_response["given_name"], userinfo_response["family_name"])
    print(json.dumps(userinfo_response, indent=2))

    user = FlaskUser(
        id_=unique_id,
        name=user_name,
        email=user_email
        )

    if not FlaskUser.get(unique_id):
        FlaskUser.create(unique_id, user_name, user_email)

    login_user(user)

    data_file = 'data/login_info.json'
    p = Path(data_file)
    if p.exists():
        with open(data_file, 'rt') as f:
            data = json.load(f)
    else:
        data = {}

    data[login_state] = {
        'access_token': access_token,
        'user_id': unique_id,
        'email': user_email,
        'name': user_name
    }

    data[user_email] = {
        'access_token': access_token,
        'user_id': unique_id,
        'email': user_email,
        'name': user_name
    }

    if not Path(data_file).exists():
        os.makedirs(os.path.dirname(data_file))
    with open(data_file, 'wt') as f:
        json.dump(data, f, indent=2)

    return redirect(url_for("logged_in"))

#
# Decorator to allow a function to run in the background, fire-and-forget style
#
def background(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if callable(f):
            return loop.run_in_executor(None, f, *args, **kwargs)
        else:
            raise TypeError('Task must be a callable')
    return wrapped

@background
def es_store_record(index_name, doc_id, record):
    _es = None
    _es = Elasticsearch([{'host': ES_HOST, 'port': 9200}])
    try:
        print("START SEARCH SUBMISSION:", record)
        outcome = _es.index(index=index_name, id=doc_id, body=record)
        print("ELASTICSEARCH:", outcome)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

def es_delete_index():
    _es = None
    _es = Elasticsearch([{'host': ES_HOST, 'port': 9200}])
    _es.indices.delete(index=ES_INDEX, ignore=[400, 404])


##################################################
# The main data storage part
##################################################
class GraphDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    #
    # For the whole system, yield a tuple of the (username, numFiles, lastSynctime)
    #
    def getAllUsers(self):
        with self.driver.session() as session:
            results = session.run("MATCH (n:ObservedFile) "
                                  "RETURN n.username, count(n), max(n.sync_time)")

            for username, numFiles, lastSync in results:
                yield (username, numFiles, lastSync)

            session.close()

    #
    # For a particular user, yield a tuple of the file hash, name, size, modifiedTime, and syncTime
    # REMIND: currently broken --- shouldn't do file_hash
    #
    def getUserDetails(self, username):
        with self.driver.session() as session:
            resultPairs = session.run("MATCH (a:ObservedFile {latest: 1}) "
                                      "WHERE a.username = $username "
                                      "RETURN a.id, a.filename, a.file_size, a.modified, a.sync_time",
                                     username = username)

            for id, fn, fs, m, st in resultPairs:
                yield (id, fn, fs, m, st)

            session.close()

    #
    #
    #
    def getDatasetInfoByUser(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (d:Dataset {latest: 1, owner: $username}) "
                                  "OPTIONAL MATCH (prev:Dataset)-[r:NextVersion]->(d) "
                                  "RETURN d.id, d.title, d.desc, d.modified, prev.uuid",
                                  username = username)

            for id, title, desc, modified, prevUuid in results:
                yield (id, title, desc, modified, prevUuid)

            session.close()

    #
    #
    #
    def getDatasetInfoById(self, id):
        with self.driver.session() as session:
            results = session.run("MATCH (d:Dataset {latest: 1, id: $idnum})-[r:Contains]->(b:ByteSet) "
                                  "OPTIONAL MATCH (prev:Dataset)-[r2:NextVersion]->(d) "
                                  "RETURN d.id, d.title, d.desc, d.owner, d.modified, b.md5hash, prev.uuid",
                                  idnum=int(id))
            return tuple(results.single())

    #
    #
    #
    def getDatasetInfoByUuid(self, uuid):
        with self.driver.session() as session:
            results = session.run("MATCH (d:Dataset {uuid: $uuid})-[r:Contains]->(b:ByteSet) "
                                  "OPTIONAL MATCH (d)-[r2:NextVersion]->(next:Dataset) "
                                  "OPTIONAL MATCH (prev:Dataset)-[r3:NextVersion]->(d) "
                                  "RETURN d.id, d.title, d.desc, d.owner, d.modified, b.md5hash, prev.uuid, next.uuid",
                                  uuid=uuid)
            return tuple(results.single())
            #session.close()

    #
    #
    #
    def findOutgoingSharingPairsForUser(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (f1:ObservedFile)-[r1:Contains]->(b1:ByteSet)<-[r2:Contains]-(f2:ObservedFile)  "
                                  "WHERE f1.username = $username "
                                  "AND f1.username <> f2.username "
                                  "AND f1.modified < f2.modified "
                                  "RETURN f1.filename, f1.id, f1.username, f1.modified, f2.filename, f2.id, f2.username, f2.modified",
                                  username=username)

            for srcFname, srcId, srcUser, srcTime, dstFname, dstId, dstUser, dstTime in results:
                yield (srcFname, srcId, srcUser, srcTime, dstFname, dstId, dstUser, dstTime)

            session.close()

    #
    #
    #
    def findIncomingSharingPairsForUser(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (f1:ObservedFile)-[r1:Contains]->(b1:ByteSet)<-[r2:Contains]-(f2:ObservedFile)  "
                                  "WHERE f1.username = $username "
                                  "AND f1.username <> f2.username "
                                  "AND f1.modified > f2.modified "
                                  "RETURN f1.filename, f1.id, f1.username, f1.modified, f2.filename, f2.id, f2.username, f2.modified",
                                  username=username)

            for srcFname, srcId, srcUser, srcTime, dstFname, dstId, dstUser, dstTime in results:
                yield (srcFname, srcId, srcUser, srcTime, dstFname, dstId, dstUser, dstTime)

            session.close()

    #
    #
    #
    def findNearbyBytesetFiles(self, md5):
        with self.driver.session() as session:
            results = session.run("MATCH (b1:ByteSet {md5hash: $md5hash})-[r1:JaccardMatch]->(b2:ByteSet)<-[r2:Contains]-(f1:ObservedFile) "
                                  "WHERE b1.md5hash <> b2.md5hash "
                                  "RETURN f1.filename, f1.id, f1.username, f1.latest, f1.modified",
                                  md5hash=md5)
            for localFname, localId, owner, isLatest, modified in results:
                yield (localFname, localId, owner, isLatest, modified)

    def getFileShinglePairs(self, shinglePairList):
        shingle_pairs = []
        for i in shinglePairList:
            used = set()
            for shingle in i[1]:
                if shingle not in used:
                    shingle_pairs.append((shingle, i[0]))
                    used.add(shingle)

        shingle_pairs.sort()
        return shingle_pairs

    def createDocumentDocumentList(self, shingle_pairs):
        current_shingle = ""
        low_index = -1
        document_document_shingle = []
        for k in range(0, len (shingle_pairs)):
            if shingle_pairs[k][0] != current_shingle:
                current_shingle = shingle_pairs[k][0]
                low_index = k
            else:
                for i in range(low_index, k):
                    document_document_shingle.append((shingle_pairs[i][1], shingle_pairs[k][1], current_shingle))

        document_document_shingle.sort()
        return document_document_shingle

    def getCloseMatches(self, document_document_shingle, cutoff = 0):
        total_similarity = {}
        for pair in document_document_shingle:
            docs = (pair[0], pair[1])
            if docs not in total_similarity:
                total_similarity[docs] = 0
            total_similarity[docs] += 1

        close_documents = []
        for i in total_similarity.keys():
            if total_similarity[i] > cutoff:
                close_documents.append(i)
        return close_documents

    ##
    def createNearMatches(self):
        with self.driver.session() as session:
            results = session.run("MATCH (a: ByteSet) WHERE EXISTS(a.optional_shingles) RETURN id(a), a.optional_shingles")
            fileShingleList = [tuple(x.values()) for x in results.data()]
            shingle_pairs = self.getFileShinglePairs(fileShingleList)
            document_document_shingle = self.createDocumentDocumentList(shingle_pairs)
            close_matches = self.getCloseMatches(document_document_shingle)
            print(close_matches)
            for i in close_matches:
                results = session.run("MATCH (a: ByteSet), (b: ByteSet) WHERE id(a) = " + str(i[0]) + " AND id(b) = " + str(i[1]) +
                                        " MERGE (a)-[r1:JaccardMatch]->(b)"
                                        " MERGE (b)-[r2:JaccardMatch]->(a)"
                                        " RETURN id(a)")

    #
    #
    #
    def createNearLineMatches(self):
        with self.driver.session() as session:
            results = session.run("MATCH (a: ByteSet), (b: ByteSet) "
                                  "WHERE a.md5hash <> b.md5hash "
                                  "WITH a, b, size(apoc.coll.intersection(a.line_hashes, b.line_hashes)) / apoc.convert.toFloat(size(apoc.coll.union(a.line_hashes, b.line_hashes))) as linejaccard "
                                  "WHERE linejaccard > 0.85 "
                                  "MERGE (a)-[r:LineJaccardMatch]->(b) "
                                  "RETURN id(a), id(b), linejaccard")

    ## MAKE THIS BE DONE EARLIER PUSHING THEM ONTO THIS LATER IS SLOW
    def applyFileInfoToByteSet(self):
        with self.driver.session() as session:
            results = session.run("MATCH (n:ByteSet)--(m:ObservedFile) WHERE EXISTS(m.optional_column_hashes) SET n.optional_column_hashes = m.optional_column_hashes")
            results = session.run("MATCH (n:ByteSet)--(m:ObservedFile) WHERE EXISTS(m.optional_shingles) SET n.optional_shingles = m.optional_shingles")


    def createNearColumnMatches(self):
        with self.driver.session() as session:
            results = session.run("MATCH (a: ByteSet), (b: ByteSet) "
                                  "WHERE a.md5hash <> b.md5hash AND EXISTS(a.optional_column_hashes) AND EXISTS(b.optional_column_hashes) "
                                  "WITH a, b, size(apoc.coll.intersection(a.optional_column_hashes, b.optional_column_hashes)) / apoc.convert.toFloat(size(apoc.coll.union(a.optional_column_hashes, b.optional_column_hashes))) as columnjaccard "
                                  "WHERE columnjaccard >= 0.5 "
                                  "MERGE (a)-[r:ColumnJaccardMatch]->(b) "
                                  "RETURN id(a), id(b), columnjaccard")

    #
    #
    #
    def getVersionedPairsForUser(self, username):
        with self.driver.session() as session:
            resultPairs = session.run("MATCH (cur:ObservedFile)-[r:NextVersion]->(next:ObservedFile) "
                                      "WHERE cur.username = $username "
                                      "AND next.username = $username "
                                      "RETURN cur.filename, cur.file_size, cur.modified, cur.id, next.file_size, next.modified, next.id "
                                      "ORDER BY cur.filename, next.modified",
                                      username = username)

            if resultPairs is None:
                return None
            else:
                for fname, fs1, m1, id1, fs2, m2, id2 in resultPairs:
                    yield (fname, fs1, m1, id1, fs2, m2, id2)

            session.close()

    #
    # Get details on a particular ObservedFile
    #
    def getFileObservationDetails(self, id):
        with self.driver.session() as session:
            result = session.run("MATCH (a: ObservedFile {id: $id})-[r:Contains]->(b:ByteSet) "
                                 "OPTIONAL MATCH (previous:ObservedFile)-[r1:NextVersion]->(a) "
                                 "OPTIONAL MATCH (next:ObservedFile)<-[r2:NextVersion]-(a) "
                                 "RETURN a.id, a.username, a.filename, a.modified, a.sync_time, previous.id, next.id, a.latest, b.md5hash",
                                 id=id)
            return result.single()

    #
    # Get details on a ByteSet
    #
    def getBytesetDetails(self, md5hash):
        with self.driver.session() as session:

            # Find details on this ByteSet
            bytesetinfo = session.run("MATCH (b: ByteSet {md5hash: $md5hash}) "
                                 "RETURN b.created, b.filetype",
                                md5hash=md5hash)

            # Find the ObservedFiles that contain this ByteSet.
            files = session.run("MATCH (b: ByteSet {md5hash: $md5hash})<-[r:Contains]-(o:ObservedFile) "
                                 "RETURN o.id, o.username, o.filename, o.latest, o.modified",
                                md5hash=md5hash)

            # Find the Datasets that contain this ByteSet.
            datasets = session.run("MATCH (b: ByteSet {md5hash: $md5hash})<-[r:Contains]-(d:Dataset) "
                                   "RETURN d.id, d.uuid, d.title, d.desc, d.modified, d.latest, d.owner",
                                   md5hash=md5hash)

            return (tuple(bytesetinfo.single()), [p for p in files], [d for d in datasets])

    #
    # Add new FileObservations to the store
    #
    def addObservations(self, observations):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_observations, observations)


    #
    # Add new FileObservations to the store
    #
    def addObservedProcess(self, process):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_observed_process, process)

    #
    # Static helper method
    #
    @staticmethod
    def _create_and_return_observations(tx, observations):
        for obs in observations:
            #
            # Create a FileObservation and its ByteSet when there's a predecessor AND the hash is new
            #
            txStr = ("MATCH (a:ObservedFile {filename: $filename, username: $username, latest: 1})-[r:Contains]->(b:ByteSet) "
                            "WHERE b.md5hash <> $newHash "
                            "MERGE (b2: ByteSet {md5hash: $newHash")
            for k, v in obs.get("optionalItems", {}).items():
                if k in ["column_hashes", "shingles"]:
                    txStr += ", {}: {}".format("optional_" + k, json.dumps(v))
                else:
                    txStr += ", {}: \"{}\"".format("optional_" + k, v)

            txStr += ("}) "
                            "ON CREATE SET b2.created = $sync_time, b.filetype = $filetype, b2.line_hashes = $line_hashes "
                            "CREATE (a2:ObservedFile {id: apoc.create.uuid(), filename: $filename, username: $username, latest: 1")
            for k, v in obs.get("optionalItems", {}).items():
                if k in ["column_hashes", "shingles"]:
                    txStr += ", {}: {}".format("optional_" + k, json.dumps(v))
                else:
                    txStr += ", {}: \"{}\"".format("optional_" + k, v)

            txStr += ("})-[r2:Contains]->(b2) "
                    "SET a.latest = 0, a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size, a2.knps_version = $knps_version, a2.install_id = $install_id, a2.hostname = $hostname")
            txStr += " CREATE (a)-[r3:NextVersion]->(a2) "
            txStr += "RETURN id(a2)"

            result = tx.run(txStr,
                            filename = obs["file_name"],
                            username = obs["username"],
                            newHash = obs["file_hash"],
                            modified = obs["modified"],
                            filetype = obs["filetype"],
                            file_size = obs["file_size"],
                            sync_time = obs["sync_time"],
                            line_hashes = obs["line_hashes"],
                            install_id = obs["install_id"],
                            knps_version = obs["knps_version"],
                            hostname = obs["hostname"])
            result = result.single()

            if result is None:
                # This gets run when there's no predecessor OR when the hash isn't new.
                txStr = "MERGE (b2: ByteSet {md5hash: $newHash"

                for k, v in obs.get("optionalItems", {}).items():
                    if k in ["column_hashes", "shingles"]:
                        txStr += ", {}: {}".format("optional_" + k, json.dumps(v))
                    else:
                        txStr += ", {}: \"{}\"".format("optional_" + k, v)

                txStr += ("}) "
                        "ON CREATE SET b2.created = $sync_time, b2.filetype = $filetype, b2.line_hashes = $line_hashes "
                        "MERGE (a2:ObservedFile {filename: $filename, username: $username, latest: 1")

                for k, v in obs.get("optionalItems", {}).items():
                    if k in ["column_hashes", "shingles"]:
                        txStr += ", {}: {}".format("optional_" + k, json.dumps(v))
                    else:
                        txStr += ", {}: \"{}\"".format("optional_" + k, v)

                txStr += ("})-[r2:Contains]->(b2) "
                        "ON CREATE SET a2.id = apoc.create.uuid(), a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size, a2.knps_version = $knps_version, a2.install_id = $install_id, a2.hostname = $hostname"
                        " RETURN id(a2)")

                #
                # Create a FileObservation and its ByteSet when there is no predecessor
                #
                result = tx.run(txStr,
                                filename = obs["file_name"],
                                username = obs["username"],
                                newHash = obs["file_hash"],
                                modified = obs["modified"],
                                file_size = obs["file_size"],
                                filetype = obs["filetype"],
                                sync_time = obs["sync_time"],
                                line_hashes = obs["line_hashes"],
                                install_id = obs["install_id"],
                                knps_version = obs["knps_version"],
                                hostname = obs["hostname"])

    #
    # Static helper method
    #
    @staticmethod
    def _create_and_return_observed_process(tx, process):
        txStr = """MATCH (f_out: ObservedFile {username: $username})-[r_out:Contains]->(b_out:ByteSet)
            WHERE b_out.md5hash IN $out_md5s AND f_out.filename IN $out_filenames
            MERGE (p:ObservedProcess {name: $name, username: $username, start_time: $start_time, last_update: $last_update,
                                      cmdline: $cmdline, uuid: apoc.create.uuid(),
                                      install_id: $install_id, knps_version: $knps_version, hostname: $hostname})
            CREATE (p)-[rp_out:HasOutput]->(f_out)

            WITH p
            OPTIONAL MATCH (f_in: ObservedFile {username: $username})-[r_in:Contains]->(b_in:ByteSet)
            WHERE b_in.md5hash IN $in_md5s  AND f_in.filename IN $in_filenames
            CALL apoc.do.when(
                f_in IS NOT NULL,
                'CREATE (p)-[rp_in:HasInput]->(f_in)',
                '',
                {f_in: f_in, p: p}) YIELD value

            RETURN(p)"""
        #
        # Create a FileObservation and its ByteSet when there is no predecessor
        #
        result = tx.run(txStr,
                        username = process["username"],
                        out_md5s = [x[1] for x in process['output_files']],
                        out_filenames = [x[0] for x in process['output_files']],
                        in_md5s = [x[1] for x in process['input_files']],
                        in_filenames = [x[0] for x in process['input_files']],
                        name = process["name"],
                        cmdline = ' '.join(process['cmdline']),
                        start_time = process["timestamp"],
                        last_update = process["last_update"],
                        install_id = process["install_id"],
                        knps_version = process["knps_version"],
                        hostname = process["hostname"])

    #
    # Add a new Dataset object to the store
    #
    def addDataset(self, datasetId, owner, title, desc, targetHash):
        with self.driver.session() as session:
            result = session.run("MATCH (old:Dataset {id:$id, latest:1}), (b:ByteSet {md5hash: $targetHash}) "
                                 "CREATE (new:Dataset {id:$id, uuid: apoc.create.uuid(), title:$title, owner:$owner, modified: $modified, desc:$desc, latest:1})-[r:Contains]->(b) "
                                 "SET old.latest=0 "
                                 "CREATE (old)-[r2:NextVersion]->(new)"
                                 "RETURN new.id",
                                 id=datasetId,
                                 title=title,
                                 owner=owner,
                                 desc=desc,
                                 modified=time.time(),
                                 targetHash=targetHash)

            result = result.single()
            if result is None:
                result = session.run("MATCH (b:ByteSet {md5hash: $targetHash}) "
                                     "CREATE (new:Dataset {id:$id, uuid: apoc.create.uuid(), title:$title, owner:$owner, modified:$modified, desc:$desc, latest:1})-[r:Contains]->(b) "
                                     "RETURN new.id",
                                     id=datasetId,
                                     title=title,
                                     owner=owner,
                                     desc=desc,
                                     modified=time.time(),
                                     targetHash=targetHash)

                return True

    #
    # Add a Comment to a Dataset object (REMIND: currently broken)
    #
    def addComment(self, username, filename, comment):
        with self.driver.session() as session:
            versionPredecessor = session.run("MATCH (a:ObservedFile) "
                                             "WHERE a.filename = $file_name "
                                             "AND a.username = $username "
                                             "RETURN a.id "
                                             "ORDER BY a.modified DESC LIMIT 1 ",
                                             file_name=filename,
                                             username=username)

            vpNode = versionPredecessor.single()
            if vpNode is None:
                return False
            else:
                commentResult = session.run("MATCH (a:ObservedFile {id:$curNodeId}) "
                                            "CREATE (c:Comment) SET c.comment = $commentStr "
                                            "CREATE (a)-[r:HasComment]->(c)",
                                            curNodeId=vpNode[0],
                                            commentStr=comment)
                return True

###################################################
# Manage data for front-end
###################################################
class BlobField(ma.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return base64.b64encode(value).decode('ascii')

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return base64.b64decode(value)
        except ValueError as error:
            raise ma.ValidationError("Error decoding blob") from error


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email")
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class DataContentsSchema(ma.Schema):
    class Meta:
        model = DataContents
        fields = ('id',
                  'mimetype',
                  'contents')
    contents = BlobField()

contents_schema = DataContentsSchema()

class DataVersionLightSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'comment',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested(UserSchema)
    contents = ma.Nested(DataContentsSchema)
    predecessors = ma.Nested('DataVersionLightSchema', many=True)
    generators = ma.Nested('DataVersionLightSchema', many=True)

class DataVersionFullSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'dataobject',
                  'comment',
                  'contents',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested('UserSchema')
    contents = ma.Nested('DataContentsSchema')
    dataobject = ma.Nested('DataObjectSchema', exclude=['versions'])
    predecessors = ma.Nested('DataVersionFullSchema', many=True)
    generators = ma.Nested('DataVersionFullSchema', many=True)


version_full_schema = DataVersionFullSchema()

class DataVersionSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'comment',
                  'contents',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested(UserSchema)
    contents = ma.Nested(DataContentsSchema)
    predecessors = ma.Nested('DataVersionLightSchema', many=True)
    generators = ma.Nested('DataVersionLightSchema', many=True)

version_schema = DataVersionSchema()

class DataObjectSchema(ma.Schema):
    class Meta:
        model = DataObject
        fields = ('id',
                  'name',
                  'description',
                  'owner',
                  'created',
                  'versions')

    owner = ma.Nested(UserSchema)
    versions = ma.Nested(DataVersionSchema, many=True, exclude=['contents'])


dobj_schema = DataObjectSchema()
dobjs_schema = DataObjectSchema(many=True)


class UserListResource(Resource):
    def get(self):
        users = db.query(User)
        return users_schema.dump(users)

    def post(self):
        # todo: validation & integrate signup stuff
        user = db.query(User).filter_by(email = request.json['email']).first()

        if not user:
            user = User(
                name = request.json['name'],
                email = request.json['email']
            )
            db.add(user)
            db.commit()
        return user_schema.dump(user)

api.add_resource(UserListResource, '/users')

class UserResource(Resource):
    def get(self, user_id):
        user = db.query(User).filter_by(id = user_id).first()

        if not user:
            abort(404)

        return user_schema.dump(user)

api.add_resource(UserResource, '/users/<int:user_id>')

class DataObjectsResource(Resource):
    def get(self):
        dobj = db.query(DataObject)

        return dobjs_schema.dump(dobj)


    def post(self):
        # todo: validation & integrate signup stuff
        metadata = json.load(request.files['metadata'])

        new_dobj = DataObject(
            owner_id = metadata['owner_id'],
            name = metadata['name'],
            description = metadata['description']
        )
        db.add(new_dobj)

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = metadata['datatype'],
            dataobject = new_dobj,
            predecessors = [db.query(DataVersion).get(x) for x in metadata['predecessors']]
        )
        db.add(new_version)

        if metadata.get('data', None):
            contents = json.dumps(metadata['data']).encode()
        elif request.files.get('datafile', None):
            contents = request.files['datafile'].read()
        else:
            # todo: get rid of jsondata/imgdata/etc.
            if new_version.datatype == '/datatypes/json':
                contents = json.dumps(metadata['jsondata']).encode()
            elif new_version.datatype == '/datatypes/img':
                contents = request.files['imgpath'].read()
            elif new_version.datatype == '/datatypes/pdf':
                contents = request.files['pdfpath'].read()
            elif new_version.datatype == '/datatypes/function':
                contents = json.dumps(metadata['code']).encode()
            else:
                contents = None


        new_contents = DataContents(
            mimetype = metadata['mimetype'],
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(new_dobj.id),
            'owner': new_dobj.owner.name,
            'name': new_dobj.name,
            'description': new_dobj.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }

        doc_id = 'X{}'.format(new_dobj.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(dobj_schema.dump(new_dobj))

api.add_resource(DataObjectsResource, '/dobjs')

class DataObjectResource(Resource):
    def get(self, dobj_id):
        dobj_id = int(dobj_id.replace('X', ''))
        dobj = db.query(DataObject).filter_by(id = dobj_id).first()
        if not dobj:
            abort(404)

        return jsonify(dobj_schema.dump(dobj))


api.add_resource(DataObjectResource, '/dobjs/<string:dobj_id>')

class DataVersionsResource(Resource):
    def post(self):
        # todo: validation & integrate signup stuff
        metadata = json.load(request.files['metadata'])
        dataobject = db.query(DataObject).get(metadata['dobj_id'])

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = metadata['datatype'],
            dataobject = dataobject,
            predecessors = [db.query(DataVersion).get(x) for x in metadata['predecessors']]
        )
        db.add(new_version)

        # todo: get rid of jsondata/imgdata/etc.
        if metadata.get('data', None):
            contents = json.dumps(metadata['data']).encode()
        elif request.files.get('datafile', None):
            contents = request.files['datafile'].read()
        else:
            # todo: get rid of jsondata/imgdata/etc.
            if new_version.datatype == '/datatypes/json':
                contents = json.dumps(metadata['jsondata']).encode()
            elif new_version.datatype == '/datatypes/img':
                contents = request.files['imgpath'].read()
            elif new_version.datatype == '/datatypes/pdf':
                contents = request.files['pdfpath'].read()
            elif new_version.datatype == '/datatypes/function':
                contents = json.dumps(metadata['code']).encode()
            else:
                contents = None

        new_contents = DataContents(
            mimetype = metadata['mimetype'],
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(dataobject.id),
            'owner': dataobject.owner.name,
            'name': dataobject.name,
            'description': dataobject.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }
        doc_id = 'X{}'.format(dataobject.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(version_full_schema.dump(new_version))

api.add_resource(DataVersionsResource, '/versions')

class DataVersionResource(Resource):
    def get(self, v_id):
        v = db.query(DataVersion).filter_by(id = v_id).first()
        print(v.contents.id)
        if not v:
            abort(404)

        return jsonify(version_full_schema.dump(v))

api.add_resource(DataVersionResource, '/version/<int:v_id>')

class DataContentsResource(Resource):
    def get(self, v_id):
        v = db.query(DataContents).filter_by(id = v_id).first()
        if not v:
            abort(404)

        return contents_schema.dump(v)

    def post(self):
        # todo: validation & integrate signup stuff
        # new_dobj = DataObject(
        #     owner_id = request.json['owner_id'],
        #     name = request.json['name'],
        #     description = request.json['description']
        # )
        # db.add(new_dobj)
        # db.commit()
        return dobj_schema.dump(new_dobj)

# api.add_resource(DataVersionResource, '/version')
api.add_resource(DataContentsResource, '/contents/<int:v_id>')

class FunctionsResource(Resource):
    def get(self):
        dobj = db.query(DataObject).filter(DataObject.versions.any(datatype = '/datatypes/function'))

        return dobjs_schema.dump(dobj)

api.add_resource(FunctionsResource, '/functions')


class FunctionResource(Resource):
    def get(self, f_id, dobj_id):
        # params = ['fips_txt', 'Median_Household_Income_2019']
        params = request.args.get('params', '').strip()

        if params:
            params = [x.strip() for x in params.split(',')]

        output = execute_function(f_id, [dobj_id], params)

        output['contents'] = base64.b64encode(output['contents']).decode('ascii')

        return output

    def post(self, f_id, dobj_id):
        metadata = json.load(request.files['metadata'])

        params = metadata.get('params', '').strip()

        if params:
            params = [x.strip() for x in params.split(',')]

        output = execute_function(f_id, [dobj_id], params)

        func = db.query(DataObject).get(f_id)

        # TODO: abstract the data object creation out, since we have it in here multiple times
        new_dobj = DataObject(
            owner_id = metadata['owner_id'],
            name = metadata['name'],
            description = metadata['description']
        )
        db.add(new_dobj)

        datatype = metadata['datatype']
        mimetype = metadata['mimetype']

        pred_obj = db.query(DataObject).get(dobj_id)
        predecessors = [pred_obj.versions[0]]

        if type(output) != str:
            if output.get('datatype', None):
                datatype = output.get('datatype', None)
            if output.get('mimetype', None):
                mimetype = output.get('mimetype', None)
            if output.get('predecessors', None):
                p_ids = output.get('predecessors', [])
                for p in p_ids:
                    pred_obj = db.query(DataObject).get(p)
                    predecessors.append(pred_obj.versions[0])

        print(predecessors)

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = datatype,
            dataobject = new_dobj,
            predecessors = predecessors,
            generators = [func.versions[0]]
        )
        db.add(new_version)

        # TODO: Clean this up
        if new_version.datatype == '/datatypes/json':
            contents = json.dumps(output).encode()
        elif new_version.datatype == '/datatypes/img':
            contents = output['contents']
        elif new_version.datatype == '/datatypes/pdf':
            contents = output['contents']
        elif new_version.datatype == '/datatypes/function':
            contents = output.encode()
        elif new_version.datatype == '/datatypes/xml':
            contents = output.encode()
        else:
            contents = output['contents']


        new_contents = DataContents(
            mimetype = mimetype,
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(new_dobj.id),
            'owner': new_dobj.owner.name,
            'name': new_dobj.name,
            'description': new_dobj.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }

        doc_id = 'X{}'.format(new_dobj.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(dobj_schema.dump(new_dobj))


api.add_resource(FunctionResource, '/function/<int:f_id>/<int:dobj_id>')

class SearchIndexResource(Resource):
    def get(self):
        return ES_INDEX

api.add_resource(SearchIndexResource, '/searchindex')


##########################################################
# HTTP Access for the instrumentation client and debugging
##########################################################
#
# Show a list of users and their high-level stats
#
@app.route("/")
def hello():
    out = "<table border=1 cellpadding=5>"
    out += "<tr><td>Name</td><td># Files</td><td>Last Sync</td></tr>"

    for username, numFiles, syncTime in GDB.getAllUsers():
        sync_date = datetime.datetime.fromtimestamp(syncTime).strftime('%Y-%m-%d %H:%M:%S')
        out += "<tr><td><a href='/user/{}'>{}</a></td><td>{}</td><td>{}</td></tr>".format(username, username, numFiles, sync_date)
    out += "</table>"

    return f'<h2>KNPS Users</h2></br>{out}'

#
# Show all the details for a particular user's files
#
@app.route('/user/<username>')
def show_user_profile(username):
    out = '<a href="/">Back to user listing</a>'

    #
    # Basic file listing
    #
    out += "<h2>All files</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td>Filename</td><td>Size</td><td>Last Modified</td><td>Last Sync</td><td># optional fields</td><td>Other Users</td></tr>"
    maxItems = 10
    count = 0
    for fileId, fname, fsize, modified, synctime in GDB.getUserDetails(username):
        mod_date = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
        sync_date = datetime.datetime.fromtimestamp(synctime).strftime('%Y-%m-%d %H:%M:%S')

        out += '<tr><td><a href="/file/{}">{}</a></td><td>{} B</td><td>{}</td><td>{}</td><td></td><td></td></tr>'.format(fileId, fname, fsize, mod_date, sync_date)

        count += 1
        if count > maxItems:
            out += "<tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>"
            break
    out += "</table>"

    #
    # Basic Dataset listing
    #
    out += "<p>"
    out += "<h2>All datasets</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td>Dataset</td><td>Last Modified</td></tr>"
    for datasetId, datasetTitle, desc, datasetModified, prevUuid in GDB.getDatasetInfoByUser(username):
        out += '<tr><td><a href="/datasetbyid/{}">{}</a></td>'.format(datasetId, datasetTitle)
        out += '<td>{}</td></tr>'.format(datetime.datetime.fromtimestamp(datasetModified).strftime('%Y-%m-%d %H:%M:%S'))
    out += "</table>"

    #
    # Identify recent changes
    #
    out += "<p>"
    out += "<h2>Recent changes</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Size 1</b></td><td><b>Last Modified 1</b></td><td><b>Size 2</b></td><td><b>Last Modified 2</b></td></tr>"
    for fname, s1, lm1, oldId, s2, lm2, newId in GDB.getVersionedPairsForUser(username):
        out += "<tr><td><a href='/file/{}'>{}</a></td>".format(newId, fname)
        out += "<td>{}</td>".format(s1)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(lm1).strftime('%Y-%m-%d %H:%M:%S'))
        out += "<td>{}</td>".format(s2)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(lm2).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"

    #
    # Identify outgoing sharing events
    #
    out += "<p>"
    out += "<h2>Likely outgoing sharing events</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Local filename</b></td><td><b>Local modified</b></td><td><b>Partner filename</b></td><td><b>Partner user</b></td><td><b>Partner modified</b></td></tr>"
    for srcFname, srcFileId, srcUser, srcTime, dstFname, dstFileId, dstUser, dstTime in GDB.findOutgoingSharingPairsForUser(username):
        out += '<tr><td><a href="/file/{}">{}</a></td>'.format(srcFileId, srcFname)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(srcTime).strftime('%Y-%m-%d %H:%M:%S'))
        out += '<td><a href="/file/{}">{}</a></td>'.format(dstFileId, dstFname)
        out += '<td><a href="/user/{}">{}</td>'.format(dstUser, dstUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(dstTime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"

    #
    # Identify incoming sharing events
    #
    out += "<p>"
    out += "<h2>Likely incoming sharing events</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Local filename</b></td><td><b>Local modified</b></td><td><b>Partner filename</b></td><td><b>Partner user</b></td><td><b>Partner modified</b></td></tr>"
    for localFname, localFileId, localUser, localTime, shareFname, shareFileId, shareUser, shareTime in GDB.findIncomingSharingPairsForUser(username):
        out += '<tr><td><a href="/file/{}">{}</a></td>'.format(localFileId, localFname)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S'))
        out += '<td><a href="/file/{}">{}</a></td>'.format(shareFileId, shareFname)
        out += '<td><a href="/user/{}">{}</td>'.format(shareUser, shareUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(shareTime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"

    return f'User {escape(username)} <br> {out}'


#
# Show the details of a particular ByteSet
#
@app.route('/byteset/<md5>')
def show_byteset(md5):
    out = '<a href="/">Back to user listing</a>'
    out += "<h1>ByteSet {}</h1>".format(md5)

    bytesetInfo, fileinfo, datasetInfo = GDB.getBytesetDetails(md5)
    bytesetCreated, bytesetFormat = bytesetInfo

    out += "<p>"
    out += "<h2>Created on: {}</h2>".format(datetime.datetime.fromtimestamp(bytesetCreated).strftime('%Y-%m-%d %H:%M:%S'))
    out += "<p>"
    out += "<h2>Data format: {}</h2>".format(bytesetFormat)
    out += "<p>"
    out += "<h2>Files that currently contain this ByteSet</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Owner</b></td></tr>"
    for fileid, username, filename, isLatest, modified in fileinfo:
        obsoleteComment = " (Obsolete)"
        if isLatest:
            obsoleteComment = ""
        out += "<tr><td><a href='/file/{}'>{}</a>{}</td><td><a href='/user/{}'>{}</a></td></tr>".format(fileid, filename, obsoleteComment, username, username)
    out += "</table>"

    #
    # Identify near-hit ByteSets
    #
    out += "<p>"
    out += "<h2>Files that currently contain near-duplicates of this ByteSet</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Owner</b></td></tr>"
    for localFname, localFileId, owner, isLatest, modified in GDB.findNearbyBytesetFiles(md5):
        out += '<tr><td><a href="/file/{}">{}</a></td>'.format(localFileId, localFname)
        out += '<td><a href="/user/{}">{}</a></td>'.format(owner, owner)
        out += '</tr>'
    out += "</table>"

    #
    # Identify relevant Datasets
    #
    out += "<p>"
    out += "<h2>Datasets that currently contain these ByteSet</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Dataset title</b></td><td><b>Dataset desc</b></td></tr>"
    for id, uuid, title, desc, modified, isLatest, owner in datasetInfo:
        out += '<tr><td><a href="/datasetbyuuid/{}">{}</a></td><td>{}</td></tr>'.format(uuid, title, desc)
    out += "</table>"

    return f'<br> {out}'


#
# Show the details of a particular ByteSet
#
@app.route('/bytesetdata/<md5>')
def show_bytesetdata(md5):
    bytesetInfo, fileinfo, datasetInfo = GDB.getBytesetDetails(md5)
    bytesetCreated, bytesetFormat = bytesetInfo

    bytesetObj = {}
    bytesetObj["id"] = md5
    bytesetObj["created"] = datetime.datetime.fromtimestamp(bytesetCreated).strftime('%Y-%m-%d %H:%M:%S')
    bytesetObj["format"] = bytesetFormat

    files = []
    for fileid, owner, filename, isLatest, modified in fileinfo:
        files.append({"fileid": fileid,
                      "owner": owner,
                      "filename": filename,
                      "modified": datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'),
                      "isLatest": isLatest})
    bytesetObj["files"] = files

    nearDuplicates = []
    for localFname, localFileId, owner, isLatest, modified in GDB.findNearbyBytesetFiles(md5):
        nearDuplicates.append({"fileid": localFileId,
                               "owner": owner,
                               "filename": localFname,
                               "modified": datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'),
                               "isLatest": isLatest})
    bytesetObj["nearDuplicates"] = nearDuplicates

    datasets = []
    for id, uuid, title, desc, modified, isLatest, owner in datasetInfo:
        datasets.append({"id": id,
                         "uuid": uuid,
                         "title": title,
                         "owner": owner,
                         "modified": datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'),
                         "isLatest": isLatest,
                         "desc": desc})
    bytesetObj["datasets"] = datasets

    return json.dumps(bytesetObj)


#
# Show all the details for a particular Dataset
#
@app.route('/datasetbyid/<id>')
def show_datasetbyid(id):
    out = '<a href="/">Back to user listing</a>'

    id, title, desc, owner, modified, bytesetMd5, prevUuid = GDB.getDatasetInfoById(id)

    out += "<h1>{} (X{})</h1>".format(title, id)
    out += "<p>"
    out += "<h3>{}</h3>".format(desc)
    out += "<p>"
    out += '<h3>Owner: <a href="/user/{}">{}</a></h3>'.format(owner, owner)
    out += "<p>"
    out += "<h3>Modified: {}</h3>".format(datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'))
    out += "<p>"
    out += '<h3>Contains ByteSet <a href="/byteset/{}">{}</a></h3>'.format(bytesetMd5, bytesetMd5)

    if prevUuid:
        out += '<a href="/datasetbyuuid/{}">Previous version.</a><p>'.format(prevUuid)
    else:
        out += 'This is the first version of the Dataset.<p>'

    out += 'This is the most recent version of the Dataset.<p>'


    return out

#
# Show all the details for a particular Dataset
#
@app.route('/datasetbyuuid/<uuid>')
def show_datasetbyuuid(uuid):
    out = '<a href="/">Back to user listing</a>'

    id, title, desc, owner, modified, bytesetMd5, prevUuid, nextUuid = GDB.getDatasetInfoByUuid(uuid)

    out += "<h1>{} (X{})</h1>".format(title, id)
    out += "<p>"
    out += "<h3>{}</h3>".format(desc)
    out += "<p>"
    out += '<h3>Owner: <a href="/user/{}">{}</a></h3>'.format(owner, owner)
    out += "<p>"
    out += "<h3>Modified: {}</h3>".format(datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'))
    out += "<p>"
    out += '<h3>Contains ByteSet <a href="/byteset/{}">{}</a></h3>'.format(bytesetMd5, bytesetMd5)

    if prevUuid:
        out += '<a href="/datasetbyuuid/{}">Previous version.</a><p>'.format(prevUuid)
    else:
        out += 'This is the first version of the Dataset.<p>'

    if nextUuid:
        out += '<a href="/datasetbyuuid/{}">Next version.</a><p>'.format(nextUuid)
    else:
        out += 'This is the most recent version of the Dataset.<p>'

    return out


#
# Show the details of a particular ObservedFile
#
@app.route('/file/<fileid>')
def show_file(fileid):
    out = ''

    foundFile = GDB.getFileObservationDetails(fileid)
    if foundFile is None:
        out += '<h1>That file cannot be found</h1>'
        return out

    fileId, username, filename, modified, synctime, prevId, nextId, latest, md5hash = foundFile
    out += '<a href="/user/{}">Back to user {}</a><p>'.format(username, username)

    modified_str = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
    synctime_str = datetime.datetime.fromtimestamp(synctime).strftime('%Y-%m-%d %H:%M:%S')

    out += "<h1>{}</h1>".format(filename)
    out += "<h3>ID {}</h3>".format(fileId)
    out += '<h3>Last modified on {}. First seen on {}</h3><p>'.format(modified_str, synctime_str)
    out += '<p>'
    out += '<h3>Contains ByteSet <a href="/byteset/{}">{}</a></h3>'.format(md5hash, md5hash)
    out += '<p>'
    out += '<h3>Owned by <a href="/user/{}">{}</a></h3>'.format(username, username)
    out += '<p>'
    if prevId:
        out += '<a href="/file/{}">Previous version.</a> '.format(prevId)
    else:
        out += 'This is the first version of the file observed. '

    if nextId:
        out += '<a href="/file/{}">Next version</a><p>'.format(nextId)
    else:
        out += 'This is the most recent version of the file observed<p>'

    out += "<p>"
    out += "<h2>Files that are currently near-duplicates of this File</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Owner</b></td></tr>"
    for localFname, localFileId, owner, isLatest, modified in GDB.findNearbyBytesetFiles(md5hash):
        out += '<tr><td><a href="/file/{}">{}</a></td>'.format(localFileId, localFname)
        out += '<td><a href="/user/{}">{}</a></td>'.format(owner, owner)
        out += '</tr>'
    out += "</table>"

    return out

#
# Show the details of a particular ObservedFile
#
@app.route('/knownlocationdata/<fileid>')
def show_knownlocationdata(fileid):
    foundFile = GDB.getFileObservationDetails(fileid)

    fileId, owner, filename, modified, synctime, prevId, nextId, isLatest, md5hash = foundFile

    modified_str = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
    synctime_str = datetime.datetime.fromtimestamp(synctime).strftime('%Y-%m-%d %H:%M:%S')

    kl = {"id": fileid,
          "owner": owner,
          "filename": filename,
          "modified": modified_str,
          "synctime": synctime_str,
          "prevId": str(prevId) if prevId else "",
          "nextId": str(nextId) if nextId else "",
          "isLatest": isLatest,
          "md5hash": md5hash}

    nearDuplicates = []
    for localFname, localFileId, owner, isLatest, modified in GDB.findNearbyBytesetFiles(md5hash):
        nearDuplicates.append({"fileid": localFileId,
                               "owner": owner,
                               "filename": localFname,
                               "modified": datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'),
                               "isLatest": isLatest})
    kl["nearDuplicates"] = nearDuplicates

    return json.dumps(kl)

#
# Accept an upload of a set of file observations
#
@app.route('/synclist/<username>', methods=['POST'])
def sync_filelist(username):
    syncTime = time.time()

    access_token = request.form.get('access_token')
    username = request.form.get('username')

    login_file = 'data/login_info.json'.format(username)
    p = Path(login_file)
    if p.exists():
        with open(login_file, 'rt') as f:
            login_data = json.load(f)
    else:
        login_data = {}

    if 'INSECURE_TOKEN_' not in access_token: # TODO: fix this!
        if (not access_token or
            not username or
            username not in login_data or
            access_token != login_data[username].get('access_token', None)) or
            not is_access_token_valid(access_token, config["issuer"], config["client_id"])):
            return json.dumps({'error': 'Access token invalid. Please run: knps --login'})

    observations = json.load(request.files['observations'])
    observations = [x["metadata"] for x in observations]
    for obs in observations:
        obs["username"] = username
        obs["sync_time"] = syncTime

    GDB.addObservations(observations)

    ## NOTE: WE MAY NOT WANT LINE OR COLUMN MATCHES.
    # Commenting out these, since they are currently very slow.
    # These should probably happen elsewhere, anyway, since they are not
    # pertinant to the user's sync. cronjob, perhaps.
    # GDB.createNearLineMatches()
    # GDB.createNearColumnMatches()

    # TODO: Move this out of the api call.
    GDB.createNearMatches()

    # show the user profile for that user
    return json.dumps(username)

#
# Accept an upload of a set of file observations
#
@app.route('/syncprocess/<username>', methods=['POST'])
def sync_process(username):
    syncTime = time.time()

    access_token = request.form.get('access_token')
    username = request.form.get('username')

    login_file = 'data/login_info.json'.format(username)
    p = Path(login_file)

    if p.exists():
        with open(login_file, 'rt') as f:
            login_data = json.load(f)
    else:
        login_data = {}

    if 'INSECURE_TOKEN_' not in access_token: # TODO: fix this!
        if (not access_token or
            not username or
            username not in login_data or
            access_token != login_data[username].get('access_token', None)):
            #  or
            # not is_access_token_valid(access_token, config["issuer"], config["client_id"])
            return json.dumps({'error': 'Access token invalid. Please run: knps --login'})

    process_data = json.load(request.files['process'])

    print(json.dumps(process_data, indent=2, default=str))

    GDB.addObservedProcess(process_data)
    #
    # ## NOTE: WE MAY NOT WANT LINE OR COLUMN MATCHES.
    # # Commenting out these, since they are currently very slow.
    # # These should probably happen elsewhere, anyway, since they are not
    # # pertinant to the user's sync. cronjob, perhaps.
    # # GDB.createNearLineMatches()
    # # GDB.createNearColumnMatches()
    #
    # # TODO: Move this out of the api call.
    GDB.createNearMatches()

    # show the user profile for that user
    return json.dumps(username)


@app.route('/adorn/<username>', methods=['POST'])
def adorn(username):
    access_token = request.form.get('access_token')
    username = request.form.get('username')

    login_file = 'data/login_info.json'.format(username)
    p = Path(login_file)
    if p.exists():
        with open(login_file, 'rt') as f:
            login_data = json.load(f)
    else:
        login_data = {}

    if (not access_token or
        not username or
        username not in login_data or
        access_token != login_data[username].get('access_token', None) or
        not is_access_token_valid(access_token, config["issuer"], config["client_id"])):
        return json.dumps({'error': 'Access token invalid. Please run: knps --login'})

    commentStr = json.load(request.files['comment'])
    filename = json.load(request.files['filename'])

    return json.dumps(str(GDB.addComment(username, filename, commentStr)))


@app.route('/createdataset/<username>', methods=['POST'])
def createDataset(username):
    access_token = request.form.get('access_token')
    username = request.form.get('username')

    login_file = 'data/login_info.json'.format(username)
    p = Path(login_file)
    if p.exists():
        with open(login_file, 'rt') as f:
            login_data = json.load(f)
    else:
        login_data = {}

    if (not access_token or
        not username or
        username not in login_data or
        access_token != login_data[username].get('access_token', None) or
        not is_access_token_valid(access_token, config["issuer"], config["client_id"])):
        return json.dumps({'error': 'Access token invalid. Please run: knps --login'})

    id = json.load(request.files['id'])
    title = json.load(request.files['title'])
    desc = json.load(request.files['desc'])
    targetHash = json.load(request.files['targetHash'])

    return json.dumps(str(GDB.addDataset(id, username, title, desc, targetHash)))


if __name__ == '__main__':

    GDB = GraphDB("bolt://{}:{}".format(NEO4J_HOST, NEO4J_PORT), "neo4j", "password")

    app.run(debug=True, host=KNPS_SERVER_HOST, port=KNPS_SERVER_PORT)
