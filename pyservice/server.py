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
from user import User as FlaskUser

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
KNPS_SERVER_PORT = int(os.getenv('KNPS_SERVER_PORT', '8228'))

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
        idv=unique_id,
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
                                      "RETURN a.uuid, a.filename, a.file_size, a.modified, a.sync_time",
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
                                  "RETURN properties(d), prev.uuid as prevId",
                                  username = username)

            return [(x[0], x[1]) for x in results]

    #
    #
    #
    def getDatasetInfoByUser(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (d:Dataset {latest: 1, owner: $username}) "
                                  "OPTIONAL MATCH (prev:Dataset)-[r:NextVersion]->(d) "
                                  "RETURN properties(d), prev.uuid as prevId",
                                  username = username)

            return [(x[0], x[1]) for x in results]

    #
    #
    #
    def getDatasetInfoByUuid(self, uuid):
        with self.driver.session() as session:
            results = session.run("MATCH (d:Dataset {uuid: $uuid})-[r:Contains]->(b:ByteSet) "
                                  "OPTIONAL MATCH (d)-[r2:NextVersion]->(next:Dataset) "
                                  "OPTIONAL MATCH (prev:Dataset)-[r3:NextVersion]->(d) "
                                  "RETURN properties(d), b.md5hash as md5hash, prev.uuid as prevId, next.uuid as nextId",
                                  uuid=uuid)
            return results.single()

    #
    #
    #
    def findCollaborationsForUser(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (f1:ObservedFile {username: $username})-[r1:Contains]->(b1:ByteSet)<-[r2:Contains]-(f2:ObservedFile)  "
                                  "WHERE f1.username <> f2.username "
                                  "OPTIONAL MATCH (d:Dataset)-[r3:Contains]->(b1) "
                                  "RETURN properties(f1), properties(f2), properties(b1), properties(d) ",
                                  username=username)

            return [(x[0], x[1], x[2], x[3]) for x in results]

    #
    #
    #
    def findCollaborationsForByteset(self, md5hash):
        with self.driver.session() as session:
            results = session.run("MATCH (f1:ObservedFile)-[r1:Contains]->(b1:ByteSet {md5hash: $md5hash})<-[r2:Contains]-(f2:ObservedFile)  "
                                  "WHERE f1.username <> f2.username "
                                  "AND f1.modified < f2.modified "
                                  "RETURN properties(f1), properties(f2) ",
                                  md5hash=md5hash)

            return [(x[0], x[1]) for x in results]

    #
    #
    #
    def findNearbyBytesetFiles(self, md5):
        with self.driver.session() as session:
            results = session.run("MATCH (b1:ByteSet {md5hash: $md5hash})-[r1:JaccardMatch]->(b2:ByteSet)<-[r2:Contains]-(f1:ObservedFile) "
                                  "WHERE b1.md5hash <> b2.md5hash "
                                  "RETURN properties(f1)",
                                  md5hash=md5)
            return [x[0] for x in results]

    #
    #
    #
    def createNearMatches(self):
        with self.driver.session() as session:
            results = session.run("MATCH (a: ByteSet), (b: ByteSet) "
                                  "WHERE a.md5hash <> b.md5hash "
                                  "WITH a, b, size(apoc.coll.intersection(a.line_hashes, b.line_hashes)) / apoc.convert.toFloat(size(apoc.coll.union(a.line_hashes, b.line_hashes))) as jaccard "
                                  "WHERE jaccard > 0.9 "
                                  "MERGE (a)-[r:JaccardMatch]->(b) "
                                  "RETURN id(a), id(b), jaccard")
            

    def updateField(self, nodeId, field, fieldVal):
        with self.driver.session() as session:
            print("Looking for ", nodeId)
            results = session.run("MATCH (a) "
                                  "WHERE a.uuid = $uuid "
                                  "SET a." + field + " = $fieldVal "
                                  "RETURN properties(a)",
                                  uuid=nodeId,
                                  fieldVal=fieldVal)
            return results.single()[0]

    #
    # Handle Schemas
    #
    def getAllSchemas(self):
        with self.driver.session() as session:
            results = session.run("MATCH (b:Schema) "
                                  "RETURN properties(b) "
                                  "ORDER BY b.modified DESC")
            ret = [x[0] for x in results]
            for x in ret:
                x["modified"] = datetime.datetime.fromtimestamp(x["modified"]).strftime('%Y-%m-%d %H:%M:%S')
            return ret
    
    def getSchemasForNode(self, nodeId):
        with self.driver.session() as session:
            results = session.run("MATCH (a {uuid: $nodeId})-[r:HasSchema]->(b:Schema) "
                                  "RETURN properties(b) "
                                  "ORDER BY b.modified DESC",
                                  nodeId=nodeId)

            ret = [x[0] for x in results]
            for x in ret:
                x["modified"] = datetime.datetime.fromtimestamp(x["modified"]).strftime('%Y-%m-%d %H:%M:%S')
            return ret

    def addSchemaEdge(self, nodeId, schemaId):
        with self.driver.session() as session:
            results = session.run("MATCH (a:Dataset {uuid: $nodeId}), (b:Schema {uuid:$schemaId}) "
                                  "MERGE (a)-[r:HasSchema]->(b) "
                                  "RETURN properties(b)",
                                  nodeId=nodeId,
                                  schemaId=schemaId)
            return results


    #
    # Handle Quality Tests
    #
    def getAllQualityTests(self):
        with self.driver.session() as session:
            results = session.run("MATCH (b:QualityTest) "
                                  "RETURN properties(b) "
                                  "ORDER BY b.modified DESC")
            ret = [x[0] for x in results]
            for x in ret:
                x["modified"] = datetime.datetime.fromtimestamp(x["modified"]).strftime('%Y-%m-%d %H:%M:%S')
            return ret
    
    def getQualityTestsForNode(self, nodeId):
        with self.driver.session() as session:
            results = session.run("MATCH (a {uuid: $nodeId})-[r:HasQualityTest]->(b:QualityTest) "
                                  "RETURN properties(b) "
                                  "ORDER BY b.modified DESC",
                                  nodeId=nodeId)

            ret = [x[0] for x in results]
            for x in ret:
                x["modified"] = datetime.datetime.fromtimestamp(x["modified"]).strftime('%Y-%m-%d %H:%M:%S')
            return ret

    def addQualityTestEdge(self, nodeId, qualityTestId):
        with self.driver.session() as session:
            results = session.run("MATCH (a:Dataset {uuid: $nodeId}), (b:QualityTest {uuid:$qualityTestId}) "
                                  "MERGE (a)-[r:HasQualityTest]->(b) "
                                  "RETURN properties(b)",
                                  nodeId=nodeId,
                                  qualityTestId=qualityTestId)
            return results


    #
    # Handle Comments
    #
    def getCommentsForNode(self, nodeId):
        with self.driver.session() as session:
            results = session.run("MATCH (a {uuid: $nodeId})-[r:HasComment]->(b:Comment) "
                                  "RETURN properties(b) "
                                  "ORDER BY b.modified DESC",
                                  nodeId=nodeId)

            ret = [x[0] for x in results]
            for x in ret:
                x["modified"] = datetime.datetime.fromtimestamp(x["modified"]).strftime('%Y-%m-%d %H:%M:%S')
            return ret

    def addComment(self, nodeId, commentStr):
        with self.driver.session() as session:
            results = session.run("MATCH (a {uuid: $nodeId}) "
                                  "CREATE (a)-[r:HasComment]->(b:Comment {uuid: apoc.create.uuid(), comment: $commentStr, owner: $owner, modified: $modified}) "
                                  "RETURN b",
                                  nodeId=nodeId,
                                  commentStr=commentStr,
                                  owner="",
                                  modified=time.time())
            return results

    #
    #
    #
    def getVersionedPairsForUser(self, username):
        with self.driver.session() as session:
            resultPairs = session.run("MATCH (cur:ObservedFile)-[r:NextVersion]->(next:ObservedFile) "
                                      "WHERE cur.username = $username "
                                      "AND next.username = $username "
                                      "RETURN cur.filename, cur.file_size, cur.modified, cur.uuid, next.file_size, next.modified, next.uuid "
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
            result = session.run("MATCH (a: ObservedFile {uuid: $id})-[r:Contains]->(b:ByteSet) "
                                 "OPTIONAL MATCH (previous:ObservedFile)-[r1:NextVersion]->(a) "
                                 "OPTIONAL MATCH (next:ObservedFile)<-[r2:NextVersion]-(a) "
                                 "RETURN a.uuid, a.username, a.filename, a.modified, a.sync_time, previous.uuid, next.uuid, a.latest, b.md5hash",
                                 id=id)
            return result.single()


    #
    # Get details on a user's ObservedFiles
    #
    def getFileObservationDetailsByUser(self, username):
        with self.driver.session() as session:
            result = session.run("MATCH (a: ObservedFile {username: $username, latest: 1}) "
                                 "OPTIONAL MATCH (previous:ObservedFile)-[r1:NextVersion]->(a) "
                                 "RETURN properties(a), previous.uuid as prevId",
                                 username=username)
            return [(x[0], x[1]) for x in result]


    #
    # Get details on a ByteSet
    #
    def getBytesetDetails(self, md5hash):
        with self.driver.session() as session:

            # Find details on this ByteSet
            bytesetinfo = session.run("MATCH (b: ByteSet {md5hash: $md5hash}) "
                                 "RETURN properties(b)",
                                md5hash=md5hash)

            # Find the ObservedFiles that contain this ByteSet.
            files = session.run("MATCH (b: ByteSet {md5hash: $md5hash})<-[r:Contains]-(o:ObservedFile) "
                                 "RETURN properties(o)",
                                md5hash=md5hash)

            # Find the Datasets that contain this ByteSet.
            datasets = session.run("MATCH (b: ByteSet {md5hash: $md5hash})<-[r:Contains]-(d:Dataset) "
                                   "RETURN properties(d)",
                                   md5hash=md5hash)

            # Find Datasets for nearby data
            #nearbyDatasets = session.run("MATCH (b: ByteSet {md5hash: $md5hash})-[r1:JaccardMatch]->(b2: ByteSet)<-[r2:Contains]-(d:Dataset) "
            #                             "WHERE NOT exists((d)-[r3:Contains]->(b)) "
            #                             "RETURN properties(d)",
            #                             md5hash=md5hash)

            # Find Datasets for ancestor data
            #nearbyDatasets = session.run("MATCH (d: ByteSet {md5hash: $md5hash})<-[r1:Contains]-(f1: ObservedFile)-[r2:NextVersion]->(f2:ObservedFile)<-[r3:Contains]-(d: Dataset) "
            #                             "WHERE NOT exists((d)-[r3:Contains]->(b)) "
            #                             "RETURN properties(d)",
            #                             md5hash=md5hash)
            

            return (bytesetinfo.single()[0], [p[0] for p in files], [d[0] for d in datasets])

    #
    # Add new FileObservations to the store
    #
    def addObservations(self, observations):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_observations, observations)

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
                            "MERGE (b2: ByteSet {md5hash: $newHash}) "
                            "ON CREATE SET b2.created = $sync_time, b.filetype = $filetype, b2.line_hashes = $line_hashes "
                            "CREATE (a2:ObservedFile {uuid: apoc.create.uuid(), filename: $filename, username: $username, latest: 1})-[r2:Contains]->(b2) "
                            "SET a.latest = 0, a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size, a2.knps_version = $knps_version, a2.install_id = $install_id, a2.hostname = $hostname")
            for k, v in obs.get("optionalItems", {}).items():
                txStr += ", a2.{}=\"{}\"".format("optional_" + k, v)
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
                txStr = ("MERGE (b2: ByteSet {md5hash: $newHash}) "
                        "ON CREATE SET b2.created = $sync_time, b2.filetype = $filetype, b2.line_hashes = $line_hashes "
                        "MERGE (a2:ObservedFile {filename: $filename, username: $username, latest: 1})-[r2:Contains]->(b2) "
                        "ON CREATE SET a2.uuid = apoc.create.uuid(), a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size, a2.knps_version = $knps_version, a2.install_id = $install_id, a2.hostname = $hostname")

                for k, v in obs.get("optionalItems", {}).items():
                    txStr += ", a2.{}=\"{}\"".format("optional_" + k, v)
                txStr += " RETURN id(a2)"
                
                
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
    # Add a new Dataset object to the store
    #
    def addDatasetVersion(self, prevId, owner, title, desc, targetHash):
        with self.driver.session() as session:
            result = session.run("MATCH (old:Dataset {uuid:$prevId, latest:1}), (b:ByteSet {md5hash: $targetHash}) "
                                 "CREATE (new:Dataset {uuid: apoc.create.uuid(), title:$title, owner:$owner, modified: $modified, desc:$desc, latest:1})-[r:Contains]->(b) "
                                 "SET old.latest=0 "
                                 "CREATE (old)-[r2:NextVersion]->(new)"
                                 "RETURN new.uuid",
                                 prevId=prevId,
                                 title=title,
                                 owner=owner,
                                 desc=desc,
                                 modified=time.time(),
                                 targetHash=targetHash)
            
            return result.single()

    def addNewDataset(self, owner, title, desc, targetHash):
        with self.driver.session() as session:        
            result = session.run("MATCH (b:ByteSet {md5hash: $targetHash}) "
                                 "CREATE (new:Dataset {uuid: apoc.create.uuid(), title:$title, owner:$owner, modified:$modified, desc:$desc, latest:1})-[r:Contains]->(b) "
                                 "RETURN properties(new)",
                                 title=title,
                                 owner=owner,
                                 desc=desc,
                                 modified=time.time(),                                     
                                 targetHash=targetHash)

            return result.single()[0]
                

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


#class UserListResource(Resource):
#    def get(self):
#        users = db.query(User)
#        return users_schema.dump(users)

#    def post(self):
#        # todo: validation & integrate signup stuff
#        user = db.query(User).filter_by(email = request.json['email']).first()#
#
#        if not user:
#            user = User(
#                name = request.json['name'],
#                email = request.json['email']
#            )
#            db.add(user)
#            db.commit()
#        return user_schema.dump(user)

#api.add_resource(UserListResource, '/users')
#
#class UserResource(Resource):
#    def get(self, user_id):
#        user = db.query(User).filter_by(id = user_id).first()#
#
#        if not user:
#            abort(404)#
#
#        return user_schema.dump(user)

#api.add_resource(UserResource, '/users/<int:user_id>')

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
# REST access for the KNPS Knowledge Graph
##########################################################

#
# Show all the details for a particular user's files
#
@app.route('/userdata/<username>')
def show_userdata(username):
    # Get the user's current ObservedFiles, Datasets, and likely collaborations
    datasetInfo = GDB.getDatasetInfoByUser(username)
    for ds, prevId in datasetInfo:
        ds["prevId"] = str(prevId) if prevId else ""

    fileInfo = GDB.getFileObservationDetailsByUser(username)
    for of, prevId in datasetInfo:
        ds["prevId"] = str(prevId) if prevId else ""

    collaborations = GDB.findCollaborationsForUser(username)
    
    kl = {"ds": [x[0] for x in datasetInfo],
          "of": [x[0] for x in fileInfo],
          "collabs": [{"userfile": x[0], "remotefile": x[1], "bs": x[2], "ds": x[3]} for x in collaborations],
          }
    return json.dumps(kl)


#
# MANAGE BYTESETS
#
@app.route('/bytesetdata/<md5>')
def show_bytesetdata(md5):
    bytesetInfo, containingFiles, containingDatasets = GDB.getBytesetDetails(md5)

    bytesetInfo["created"] = datetime.datetime.fromtimestamp(bytesetInfo["created"]).strftime('%Y-%m-%d %H:%M:%S')

    for cf in containingFiles:
        cf["modified"] = datetime.datetime.fromtimestamp(cf["modified"]).strftime('%Y-%m-%d %H:%M:%S')

    for cd in containingDatasets:
        cd["modified"] = datetime.datetime.fromtimestamp(cd["modified"]).strftime('%Y-%m-%d %H:%M:%S')

    nearbyFiles = GDB.findNearbyBytesetFiles(md5)
    for nf in nearbyFiles:
        nf["modified"] = datetime.datetime.fromtimestamp(nf["modified"]).strftime('%Y-%m-%d %H:%M:%S')

    likelyCollaborations = GDB.findCollaborationsForByteset(md5)

    bytesetInfo["files"] = containingFiles
    bytesetInfo["datasets"] = containingDatasets    
    bytesetInfo["nearDuplicates"] = nearbyFiles
    bytesetInfo["likelyCollaborations"] = [{"user1": x[0], "user2": x[1]} for x in likelyCollaborations]

    return json.dumps(bytesetInfo)


#
# MANAGE OBSERVEDFILEs
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
          "latest": isLatest,
          "md5hash": md5hash}

    nearbyFiles = GDB.findNearbyBytesetFiles(md5hash)
    for nf in nearbyFiles:
        nf["modified"] = datetime.datetime.fromtimestamp(nf["modified"]).strftime('%Y-%m-%d %H:%M:%S')

    kl["nearDuplicates"] = nearbyFiles

    return json.dumps(kl)


#
# MANAGE DATASETS
#
@app.route('/dataset/<id>')
def show_datasetdata(id):
    #uuid, title, desc, owner, modified, isLatest, md5hash, prevId, nextId = GDB.getDatasetInfoByUuid(id)
    kl, md5hash, prevId, nextId = GDB.getDatasetInfoByUuid(id)
    kl["modified"] = datetime.datetime.fromtimestamp(kl["modified"]).strftime('%Y-%m-%d %H:%M:%S')
    kl["md5hash"] = md5hash
    kl["prevId"] = str(prevId) if prevId else ""
    kl["nextId"] = str(nextId) if nextId else ""    

    return json.dumps(kl)

@app.route('/nodeedit/<id>', methods=["POST"])
def edit_nodedata(id):
    incomingNode = json.loads(request.get_json())
    result = GDB.updateField(incomingNode["uuid"], incomingNode["field"], incomingNode["value"])
    return json.dumps(result)

@app.route('/createdatasetfrombyteset/<md5>', methods=["POST"])
def add_dataset(md5):
    incomingData = json.loads(request.get_json())
    kl  = GDB.addNewDataset(incomingData["user"], "Default Title", "Default Description", md5)

    kl["modified"] = datetime.datetime.fromtimestamp(kl["modified"]).strftime('%Y-%m-%d %H:%M:%S')
    kl["md5hash"] = md5
    kl["prevId"] = ""
    kl["nextId"] = ""    

    return json.dumps(kl)

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

#
# MANAGE SCHEMAS
#
@app.route('/schemas/<id>')
def get_schemas(id):
    kl = {"schemas": GDB.getSchemasForNode(id)}
    return json.dumps(kl)

@app.route('/allschemas')
def get_all_schemas():
    kl = {"schemas": GDB.getAllSchemas()}
    return json.dumps(kl)

@app.route('/addschemaedge/<id>', methods=["POST"])
def add_schema_edge(id):
    incomingReq = json.loads(request.get_json())
    result = GDB.addSchemaEdge(id, incomingReq["targetSchema"])
    return get_schemas(id)

#
# MANAGE QUALITY TESTS
#
@app.route('/qualitytests/<id>')
def get_qualitytests(id):
    kl = {"qualitytests": GDB.getQualityTestsForNode(id)}
    return json.dumps(kl)

@app.route('/allqualitytests')
def get_all_qualitytests():
    kl = {"qualitytests": GDB.getAllQualityTests()}
    return json.dumps(kl)

@app.route('/addqualitytestedge/<id>', methods=["POST"])
def add_qualitytest_edge(id):
    incomingReq = json.loads(request.get_json())
    result = GDB.addQualityTestEdge(id, incomingReq["targetQualityTest"])
    return get_qualitytests(id)


#
# MANAGE COMMENTS
#
@app.route('/comments/<id>')
def get_comments(id):
    kl = {"comments": GDB.getCommentsForNode(id)}
    return json.dumps(kl)

@app.route('/addcomment/<id>', methods=["POST"])
def add_comment(id):
    incomingReq = json.loads(request.get_json())
    result = GDB.addComment(incomingReq["uuid"], incomingReq["value"])
    return get_comments(incomingReq["uuid"])

#
# UPLOADS: Accept an upload of a set of file observations
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

    if (not access_token or
        not username or
        username not in login_data or
        access_token != login_data[username].get('access_token', None) or
        not is_access_token_valid(access_token, config["issuer"], config["client_id"])):
        return json.dumps({'error': 'Access token invalid. Please run: knps --login'})

    observations = json.load(request.files['observations'])
    observations = [x["metadata"] for x in observations]
    for obs in observations:
        obs["username"] = username
        obs["sync_time"] = syncTime

    GDB.addObservations(observations)

    #
    # This call is currently quite bad, algorithmically.
    # It will get too slow when the repository is large.
    # We need to reimplement eventually
    GDB.createNearMatches()

    # show the user profile for that user
    return json.dumps(username)



if __name__ == '__main__':
    GDB = GraphDB("bolt://{}:{}".format(NEO4J_HOST, NEO4J_PORT), "neo4j", "password")    
    
    app.run(debug=True, host=KNPS_SERVER_HOST, port=KNPS_SERVER_PORT)

    greeter.close()    
