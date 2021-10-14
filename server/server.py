import atexit
import base64
import datetime
import json
import os
from pathlib import Path
import pandas
import requests
import time
import uuid

import flask
from flask import send_from_directory
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify, abort
from flask_cors import CORS
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from threading import Lock
from okta_helpers import is_access_token_valid, is_id_token_valid, config
from user import User

from markupsafe import escape
from neo4j import GraphDatabase

from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef, Literal

from gen import ID_gen_val
from gen import ID_gen_var
from werkzeug.utils import secure_filename
from settings import SERVER_URL, SERVER_ENVIRONMENT

GDB = None

app = flask.Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.secret_key = b'\x13f0\x97\x86QUOHc\xfa\xe7(\xa1\x8d1'

m = Lock()
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png',
                      'jpg', 'jpeg', 'gif', 'csv', 'ipynb'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

server_url = SERVER_URL
app.config['SERVER_NAME'] = server_url.split('//')[1]
app.config['ENV'] = SERVER_ENVIRONMENT
if SERVER_ENVIRONMENT == 'development':
    app.config['DEBUG'] = True

g = Graph('Sleepycat', identifier="kgpl")
g.open('db', create=True)
g.bind("kg",  "{}/".format(server_url))

dg = Graph('Sleepycat', identifier="dependency")
dg.open('db', create=True)
dg.bind("kg", "{}/".format(server_url))

ns = Namespace("{}/".format(server_url))

app.config.update({'SECRET_KEY': 'SomethingNotEntirelySecret'})

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

login_manager = LoginManager()
login_manager.init_app(app)

APP_STATE = 'ApplicationStateKNPS'
NONCE = 'SampleNonceKNPS'


# predicates
hasHistory = ns.hasHistory
hasKGPLValue = ns.hasKGPLValue
valueHistory = ns.valueHistory
hasValue = ns.hasValue
kgplType = ns.kgplType
pyType = ns.pyType
hasComment = ns.hasComment
belongTo = ns.belongTo
derive = ns.derive

# kgplType
kgplValue = ns.kgplValue
kgplVariable = ns.kgplVariable


# length
LENCOM = 30

@app.route("/", methods=['GET'])
def main():
#    return "KGPL", 200
    out = "<table border=1 cellpadding=5>"
    out += "<tr><td>Name</td><td># Files</td><td>Last Sync</td></tr>"

    for username, numFiles, syncTime in GDB.getAllUsers():
        sync_date = datetime.datetime.fromtimestamp(syncTime).strftime('%Y-%m-%d %H:%M:%S')
        out += "<tr><td><a href='/user/{}'>{}</a></td><td>{}</td><td>{}</td></tr>".format(username, username, numFiles, sync_date)
    out += "</table>"

    return f'<h2>KNPS Users</h2></br>{out}'


###########################################
# Login/logout helper functions
###########################################
@app.route("/logged_in")
def logged_in():
    return '<h2>Thank you for logging in.</h2>'

@app.route("/cli_login")
def cli_login():
    print("GOT IT")
    access_token = request.args.get("access_token", None)

    if access_token and is_access_token_valid(access_token, config["issuer"], config["client_id"]):
        print ("VALID")
        pass
    else:
        login_state = 'cli_{}'.format(uuid.uuid1())

        # get request params
        query_params = {'client_id': config["client_id"],
                        'redirect_uri': config["redirect_uri"],
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

    user = User(
        id_=unique_id, name=user_name, email=user_email
    )

    if not User.get(unique_id):
        User.create(unique_id, user_name, user_email)

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

    with open(data_file, 'wt') as f:
        json.dump(data, f, indent=2)

    return redirect(url_for("logged_in"))


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
            results = session.run("MATCH (b1:ByteSet {md5hash: $md5hash})-[r1:JaccardMatch]->(b2:ByteSet)<-[r2:Contains]-(f1:ObservedFile {latest:1}) "
                                  "WHERE b1.md5hash <> b2.md5hash "
                                  "RETURN f1.filename, f1.id, f1.username",
                                  md5hash=md5)
            for localFname, localId, user in results:
                yield (localFname, localId, user)

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
                                 "RETURN o.id, o.username, o.filename, o.latest",
                                md5hash=md5hash)

            # Find the Datasets that contain this ByteSet.
            datasets = session.run("MATCH (b: ByteSet {md5hash: $md5hash, latest: 1})<-[r:Contains]-(d:Dataset) "
                                   "RETURN d.id, d.uuid, d.title, d.desc",
                                   md5hash=md5hash)

            return (tuple(bytesetinfo.single()), [p for p in files], [d for d in datasets])

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
                            "CREATE (a2:ObservedFile {id: apoc.create.uuid(), filename: $filename, username: $username, latest: 1})-[r2:Contains]->(b2) "
                            "SET a.latest = 0, a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size")
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
                            line_hashes = obs["line_hashes"])

            result = result.single()
            if result is None:
                # This gets run when there's no predecessor OR when the hash isn't new.
                txStr = ("MERGE (b2: ByteSet {md5hash: $newHash}) "
                        "ON CREATE SET b2.created = $sync_time, b2.filetype = $filetype, b2.line_hashes = $line_hashes "
                        "MERGE (a2:ObservedFile {filename: $filename, username: $username, latest: 1})-[r2:Contains]->(b2) "
                        "ON CREATE SET a2.id = apoc.create.uuid(), a2.modified = $modified, a2.sync_time = $sync_time, a2.file_size = $file_size")

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
                                line_hashes = obs["line_hashes"])

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
    maxItems = 3
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
    for fileid, username, filename, isLatest in fileinfo:
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
    for localFname, localFileId, owner in GDB.findNearbyBytesetFiles(md5):
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
    for id, uuid, title, desc in datasetInfo:
        out += '<tr><td><a href="/datasetbyuuid/{}">{}</a></td><td>{}</td></tr>'.format(uuid, title, desc)
    out += "</table>"

    return f'<br> {out}'


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
    for localFname, localFileId, owner in GDB.findNearbyBytesetFiles(md5hash):
        out += '<tr><td><a href="/file/{}">{}</a></td>'.format(localFileId, localFname)
        out += '<td><a href="/user/{}">{}</a></td>'.format(owner, owner)
        out += '</tr>'
    out += "</table>"        


    return out
        


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


"""
@app.route("/nextval", methods=['GET'])
def return_val_id():
    vid = ID_gen_val.next()
    context = {
        "id": ns["val/" + str(vid)]
    }
    return flask.jsonify(**context), 200

"""

@app.route("/nextvar", methods=['GET'])
def return_var_id():
    vid = ID_gen_var.next()
    context = {
        # "id": "var/" + str(vid)
        # "id": ns["var/" + str(vid)]
        "id":"KNPS_"+str(vid)
    }

    return flask.jsonify(**context), 201



@app.route("/val", methods=['POST'])
def post_val():
    """
        Method for adding a new value, via POST
    """
    d = request.form
    if "val" not in d or "pyType" not in d or "comment" not in d or "user" not in d or "dependency" not in d:
        flask.abort(400)
    dependency = json.loads(d["dependency"])
    if d["pyType"] == "File":
        if "file" not in request.files:
            flask.abort(400)
        image = json.loads(d["val"])
        if "filename" not in image:
            flask.abort(400)
        if not allowed_file(image["filename"]):
            flask.abort(400)
    m.acquire()
    vid = ID_gen_val.current
    for de in dependency:
        did = int(de[de.rfind('/') + 1:])
        if did >= vid:
            flask.abort(400)
    vid = ID_gen_val.next()
    m.release()
    url = URIRef(ns["val/" + str(vid)])
    if d["pyType"] == "File":
        request.files["file"].save(os.path.join(
            app.config['UPLOAD_FOLDER'], str(vid)))
    # print(url)
    # if using different namespace for val and var, we should change ?x into kgplValue
    val = Literal(d["val"])
    pyt = Literal(d["pyType"])
    com = Literal(d["comment"])
    ownername = Literal(d["user"])
    g.add((url, belongTo, ownername))
    for de in dependency:
        durl = URIRef(de)
        dg.add((durl, derive, url))
    g.add((url, hasValue, val))
    g.add((url, kgplType, kgplValue))
    g.add((url, pyType, pyt))
    g.add((url, hasComment, com))
    context = {"url": str(url)}
    return flask.jsonify(**context), 201


@app.route("/checkvarid", methods=['POST'])
def checkvarid():
    d = request.get_json()
    if "var_id" not in d:
        flask.abort(500, "invalid post for /checkvarid")
    var_url = URIRef(ns["var/" + d["var_id"]])
    qres = g.query(
        """ASK {
            {?url kg:kgplType kg:kgplVariable}
            }
        """,
        initBindings={'url': var_url}
    )
    for x in qres:
        if not x:
            print("var id not exist")
            return '', 201
        else:
            print("var id exists")
            flask.abort(409, "var id occupied")


@app.route("/var", methods=['POST'])
def post_var():
    d = request.get_json()
    if "val_id" not in d or "comment" not in d or "user" not in d or "var_id" not in d:
        flask.abort(400, "var creation parameter not complete")
    val_url = URIRef(d["val_id"])

    # check if val_id is valid
    qres = g.query(
        """ASK {
            {?url kg:kgplType kg:kgplValue}
            }
        """,
        initBindings={'url': val_url}
    )
    for x in qres:
        if not x:
            print("val id not exist")
            flask.abort(400)
    m.acquire()
    # vid = ID_gen_var.next()
    vid = d["var_id"]
    m.release()
    url = URIRef(ns["var/" + str(vid)])
    ts = time.time()
    ts_url = URIRef(url + "/ts/" + str(ts))
    com = Literal(d["comment"])
    ownername = Literal(d["user"])
    g.add((url, belongTo, ownername))
    g.add((url, valueHistory, ts_url))
    g.add((ts_url, hasKGPLValue, val_url))
    g.add((url, kgplType, kgplVariable))
    g.add((ts_url, hasComment, com))
    context = {"url": url, "timestamp": ts}
    return flask.jsonify(**context), 201


@app.route("/load/val", methods=['GET'])
def get_val():
    vid = request.args.get('vid')
    url = URIRef(vid)
    qres = g.query(
        """SELECT ?val ?pyt ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasComment ?com ;
               kg:hasValue ?val ;
               kg:belongTo ?user .
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for val, pyt, com, user in qres:
            context = {
                "val": str(val),
                "pyt": str(pyt),
                "comment": str(com),
                "user": str(user)
            }
            dqres = dg.query(
                """SELECT ?durl
                WHERE {
                    ?durl kg:derive ?url .
                }""",
                initBindings={'url': url}
            )
            if len(dqres) == 0:
                context["dependency"] = []
            else:
                dependency = []
                for durl, in dqres:
                    dependency.append(str(durl))
                context["dependency"] = dependency
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/load/var", methods=['GET'])
def get_var():
    vid = request.args.get('vid')
    print(vid)
    url = URIRef(vid)
    # print(url)
    qres = g.query(
        """SELECT ?ts ?val_url ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                kg:belongTo ?user ;
                kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_url ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    # print(len(qres))
    if len(qres) == 1:
        for ts, val_url, com, user in qres:
            val_url = str(val_url)
            ts = str(ts)
            com = str(com)
            actual_ts = float(ts[ts.rfind('/') + 1:])
            context = {
                "val_id": val_url,
                "timestamp": actual_ts,
                "comment": com,
                "user": user
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/var", methods=['PUT'])
def set_var():
    d = request.get_json()
    if "vid" not in d or "val_id" not in d or "timestamp" not in d or "new_comment" not in d:
        flask.abort(400)
    url = URIRef(d["vid"])
    val_url = URIRef(d["val_id"])
    ts = d["timestamp"]
    # print("URI: ", url)
    qres = g.query(
        """SELECT ?ts_url
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                 kg:valueHistory ?ts_url .
        }""",
        initBindings={'url': url}
    )
    ots_url = URIRef(url+"/ts/"+str(ts))

    if len(qres) == 1:
        for ts_url, in qres:
            if ts_url != ots_url:
                print(ts_url)
                print(type(ts_url))
                print(type(ots_url))
                print(ots_url)
                print("version conflict")
                flask.abort(403)
            qres = g.query(
                """ASK {
                ?url kg:kgplType kg:kgplValue
                }""",
                initBindings={'url': val_url}
            )
            for x in qres:
                if not x:
                    print("val id not exist")
                    flask.abort(400)
            ts = time.time()
            nts_url = url+"/ts/"+str(ts)
            # nts_url = URIRef(os.path.join(url, str(ts)))
            g.remove((url, valueHistory, None))
            g.add((url, valueHistory, nts_url))
            g.add((nts_url, hasKGPLValue, val_url))
            g.add((nts_url, hasHistory, ts_url))
            g.add((nts_url, hasComment, Literal(d["new_comment"])))
            context = {"timestamp": ts}
            return flask.jsonify(**context), 201
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        print("Multiple result found!")
        return flask.abort(500)


@app.route("/gethistory", methods=['GET'])
def gethistory():
    d = request.get_json()
    if "vid" not in d:
        flask.abort(400)
    url = URIRef(d["vid"])
    qres = g.query(
        """SELECT ?ts ?val_uri
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                 kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_uri ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    rst = []
    if len(qres) != 1:
        print(len(qres))
        print("place one")
        flask.abort(500)
    for x, val_uri in qres:
        current_ts = x
        # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
        rst.append(val_uri)
        while True:
            qres = g.query(
                """SELECT ?ts ?val_uri
                WHERE {
                    ?current_ts kg:hasHistory ?ts .
                    ?ts kg:hasKGPLValue ?val_uri .
                }""",
                initBindings={'current_ts': current_ts}
            )
            if len(qres) == 0:
                break
            elif len(qres) != 1:
                print("place two")

                flask.abort(500)
            for ts, val_uri in qres:
                current_ts = ts
                # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
                rst.append(val_uri)
        context = {"list": rst}
        return flask.jsonify(**context), 200


@app.route("/getLatest", methods=['GET'])
def getLatest():
    d = request.get_json()
    if "val_id" not in d:
        flask.abort(400)

    url = ns[str(d["val_id"])]
    qres = g.query(
        """SELECT ?ts ?val_uri
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
               kg:valueHistory ?ts .
            ?ts kg:hasKGPLValue ?val_uri
        }""",
        initBindings={'url': url}
    )
    if len(qres) == 1:
        for ts, val_url in qres:
            val_url = str(val_url)
            ts = str(ts)
        actual_val_id = int(val_url[val_url.rfind('/') + 1:])
        actual_ts = float(ts[ts.rfind('/') + 1:])
        context = {
            "val_id": actual_val_id,
            "timestamp": actual_ts
        }
        return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


@app.route("/val/<vid>", methods=['GET'])
def frontend_val(vid):
    url = ns["val/" + str(vid)]

    print(url)
    qres = g.query(
        """SELECT ?val ?pyt ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplValue ;
               kg:pyType ?pyt ;
               kg:hasValue ?val ;
               kg:hasComment ?com ;
               kg:belongTo ?user.
        }""",
        initBindings={'url': url}
    )
    pandas.set_option('display.float_format', lambda x: '%.1f' % x)
    if len(qres) == 1:
        for val, pyt, com, user in qres:
            file_name = None
            current_value = pandas.read_json(val).to_html() if str(
                pyt) == "DataFrame" else str(val)

            if str(pyt) == "Relation":
                # a = json.loads(str(val))["trace"]

                # b = json.loads(a)
                # print(type(b))
                context = {
                    "KGPLValue": str(url),
                    "entity_id": json.loads(str(val))["entity_id"],
                    "Python_Type": str(pyt),
                    "Comments": str(com),
                    "Owner": str(user),
                    "df": pandas.read_json(json.loads(str(val))["df"]).to_html(),
                    "query_str": json.loads(str(val))["query_str"],
                }

                return flask.render_template("relation_val_meta_page.html", **context)
            elif str(pyt) == "File":
                file_name = vid[vid.rfind('/') + 1:]

            context = {
                "KGPLValue": str(url),
                "Current_Value": current_value,
                "Python_Type": str(pyt),
                "Comments": str(com),
                "Owner": str(user),
                "file_name": file_name
            }
            return flask.render_template("val_meta_page.html", **context)
            # return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        print("Multiple Results Found, should not happen!")
        return flask.abort(500)


@app.route("/var/<vid>", methods=['GET'])
def frontend_meta_var(vid):
    url = ns["var/" + str(vid)]
    print(url)
    his = []
    owner = ""
    qres = g.query(
        """SELECT ?ts ?val_url ?com ?user
        WHERE {
            ?url kg:kgplType kg:kgplVariable ;
                kg:valueHistory ?ts ;
                kg:belongTo ?user.
            ?ts kg:hasKGPLValue ?val_url ;
                kg:hasComment ?com .
        }""",
        initBindings={'url': url}
    )
    print("len: ", len(qres))
    if len(qres) == 1:
        for ts, val_url, com, user in qres:
            his.append(str(ts))
            val_url = str(val_url)
            ts_for_query = ts
            ts = str(ts)
            com = str(com)
            # print(val_url)
            # actual_val_id = int(val_url[val_url.rfind('/') + 1:])
            actual_ts = float(ts[ts.rfind('/') + 1:])
            owner = str(user)

            while True:
                qres = g.query(
                    """SELECT ?history ?val_uri
                    WHERE {
                        ?url kg:hasComment ?com ;
                             kg:hasHistory ?history ;
                             kg:hasKGPLValue ?val_uri .
                    }""",
                    initBindings={'url': ts_for_query}
                )
                print(ts)
                if len(qres) == 0:
                    print("end")
                    break
                elif len(qres) != 1:
                    print("place two")

                    flask.abort(500)
                for history, val_uri in qres:
                    ts_for_query = history
                    # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
                    his.append(str(history))


        context = {
            "KGPLVariable": str(url),
            "Currently_containing_KGPLValue": val_url,
            "Current_comment": com,
            "Last_modified_timestamp": actual_ts,
            "Last_modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(actual_ts)),
            "History": his,
            "Owner": str(owner)
        }
        # print("can render")
        return flask.render_template("var_meta_page.html", **context)
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


"""frontend"""


@app.route("/graph1.svg", methods=['GET'])
def get_svg():
    return flask.send_file("graph1.svg")


@app.route("/compact/<vid>", methods=['GET'])
def get_compacthtml(vid):
    url = ns["val/" + str(vid)]
    qres = g.query(
        """SELECT ?kgval ?ty ?com
        WHERE {
            ?url kg:hasValue ?kgval ;
                kg:pyType ?ty ;
                kg:hasComment ?com.
        }""",
        initBindings={'url': url}
    )
    if len(qres) != 1:
        print(url)
        return "ERROR: data not found or data found not single"
    for val, ty, com in qres:
        see_more_info = "<p> See more info <a href='val/" + \
            str(vid) + "'><u> here </u></a> </p>"
        if len(com) > 300:
            com = com[:300]
            comment = "<h3> Comment: "+com+"... </h3>"
        else:
            comment = "<h3> Comment: "+com+"</h3>"

        val = json.loads(val)
        if str(ty) == "File":
            if "filename" not in val:
                print("cannot find filename")
                flask.abort(500)
            filename = val["filename"]
            filetype = filename.rsplit('.', 1)[1].lower()
            if filetype in ['png', 'jpg', 'jpeg', 'gif']:
                header = "<h3> Data type: File</h3> <h3> URL: " + \
                    str(url) + "</h3>"
                content = "<img src='" + \
                    os.path.join(
                        app.config['UPLOAD_FOLDER'], str(vid)) + "' alt=image style='width:auto; height:200px'>"
                return json.dumps({"html": header + comment + content + see_more_info})
            else:
                header = "<h3> Data type: " + \
                    val["__file__"] + " file</h3> <h3>URL: " + \
                    str(url) + "</h3>"
                return json.dumps({"html": header + comment + see_more_info})
        elif str(ty) == "Relation":
            header = "<h3> Data type: " + \
                str(ty) + "</h3><h3> URL: " + str(url) + "</h3>"
            content = "<pre>" + \
                pandas.read_json(val["df"]).iloc[0:3].to_html() + "</pre>"
            return json.dumps({"html": header + comment + content + see_more_info})
        elif str(ty) == "DataFrame":
            return ""
        elif str(ty) == "dict":
            header = "<h3> Data type: " + \
                str(ty) + "</h3><h3> URL: " + str(url) + "</h3>\n" +\
                "<h3>"+comment+"</h3>"
            return json.dumps({"val": val, "header": header, "more_info": see_more_info})
        else:
            header = "<h3> Data type: " + \
                str(ty) + "</h3><h3> URL: " + str(url) + "</h3>"
            if str(ty) == "tuple":
                val = tuple(val)
            content = str(val)
            if len(content) > 300:
                content = content[:300]
                content = "<div id='pre_text'><pre>" + content + "...</pre></div>"
            else:
                content = "<div id='pre_text'><pre>" + content + "</pre></div>"
            return json.dumps({"html": header + comment + content + see_more_info})


@app.route("/visualization", methods=['GET'])
def visual():
    user_dict = {}
    depend_dict = {}
    current = ID_gen_val.current
    for vn in range(0, current):
        url = ns["val/" + str(vn)]
        print(url)
        qres = g.query(
            """SELECT ?user
            WHERE {
                ?url kg:belongTo ?user .
            }""",
            initBindings={'url': url}
        )

        if len(qres) != 1:
            print("user")
            flask.abort(500)
        else:
            for user, in qres:
                user_dict[vn] = str(user)
                # json["values"][str(url)] = str(user)

        depend_dict[vn] = []
        dqres = dg.query(
            """SELECT ?durl
            WHERE {
                ?durl kg:derive ?url .
            }""",
            initBindings={'url': url}
        )
        for durl, in dqres:
            src = int(str(durl)[str(durl).rfind("/") + 1:])
            depend_dict[vn].append(src)

    cluster = []
    cluster_dict = {}
    # cluster_depend = []
    for x in range(0, current):
        added = False
        if user_dict[x] == "anonymous":
            cluster.append(["anonymous", [x]])
            # cluster_depend.append("don't care")
            cluster_dict[x] = len(cluster) - 1
            continue
        lowest_level = 0
        for j in depend_dict[x]:
            if cluster_dict[j] > lowest_level:
                lowest_level = cluster_dict[j]
        for i in range(lowest_level, len(cluster)):
            l = cluster[i]
            if l[0] == user_dict[x]:
                added = True
                cluster[i][1].append(x)
                cluster_dict[x] = i
                break
            """
            if depend_dict[x] == []:
                cluster[i][1].append(x)
                added = True
                break
            depend_set = {cluster_dict[j] for j in depend_dict[x]}
            if cluster_depend < lowest_level:
                continue
            if depend_set > cluster_depend[i]:
                cluster_depend[i] = depend_set
            cluster[i][1].append(x)
            cluster_dict[x] = i
            added = True
            break
            """
        if not added:
            cluster.append([user_dict[x], [x]])
            cluster_dict[x] = len(cluster) - 1
            # cluster_depend.append({cluster_dict[j] for j in depend_dict[x]})
        """
        print(cluster)
        print(cluster_depend)
        print(cluster_dict)
        """
    with open("vis.gv", "w") as file:
        file.write("digraph G {\n")
        for i, l in enumerate(cluster):
            title = ""
            for idx, node in enumerate(l[1]):
                title += str(node)
                title += "_"
            file.write("subgraph clusterusr_" + title +
                       " {\nnode [style=filled];\ncolor=blue;\nlabel=\"" + l[0] + "\";\n")
            for node in l[1]:
                val_url = ns["val/" + str(node)]
                qres = g.query(
                    """SELECT ?var_url ?com
                    WHERE {
                        ?var_url kg:kgplType kg:kgplVariable ;
                            kg:valueHistory ?ts .
                        ?ts kg:hasKGPLValue ?val_url ;
                            kg:hasComment ?com .
                    }""",
                    initBindings={'val_url': val_url}
                )
                cqres = g.query(
                    """SELECT ?com
                        WHERE {
                            ?val_url kg:hasComment ?com .
                        }""",
                    initBindings={'val_url': val_url}
                )
                if len(qres) == 0:
                    if len(cqres) != 1:
                        flask.abort(500)
                    for com, in cqres:
                        if len(com) > LENCOM:
                            com = com[:LENCOM] + "..."
                        # file.write("subgraph clustercomment_" + str(node) +
                        #         "_ {\nnode [style=filled];\ncolor=grey;\nlabel=\"comment: " + str(com) + "\";\n")
                        file.write("\"val" + str(node) + "\" [style = \"filled\" penwidth = 1 fillcolor = \"white\" fontname = \"Courier New\" fontsize = 10 shape = \"Mrecord\" label=<<table border=\"0\" cellborder=\"0\" cellpadding=\"3\" bgcolor=\"white\"><tr><td bgcolor=\"black\" align=\"center\" colspan=\"2\"><font color=\"white\">val" + str(
                            node) + "</font></td></tr><tr><td align=\"left\" port=\"r1\" >" + str(com) + "</td></tr></table>>];\n")
                        # file.write("}\n")
                else:
                    label = ""
                    c = 1
                    for var_url, com in qres:
                        label += "label"+" " + \
                            str(var_url)[str(var_url).rfind("/") + 1:]
                        label += "\n"
                        temp = str(com)
                        if len(temp) > LENCOM:
                            temp = temp[:LENCOM] + "..."
                        label += temp
                        label += "\n"
                        if c == len(qres):
                            break
                        label += ", "
                        c += 1
                    file.write("subgraph clustervar_" + str(node) +
                               "_ {\nnode [style=filled];\nfontname=\"Courier New\";\nfontsize=10;\ncolor=black;\nlabel=\"" + label + "\";\n")
                    if len(cqres) != 1:
                        flask.abort(500)
                    for com, in cqres:
                        if len(com) > LENCOM:
                            com = com[:LENCOM] + "..."
                        # file.write("subgraph clustercomment_" + str(node) +
                        #         "_ {\nnode [style=filled];\ncolor=grey;\nlabel=\"comment: " + str(com) + "\";\n")
                        file.write("\"val" + str(node) + "\" [style = \"filled\" penwidth = 1 fillcolor = \"white\" fontname = \"Courier New\" fontsize = 8 shape = \"Mrecord\" label=<<table border=\"0\" cellborder=\"0\" cellpadding=\"3\" bgcolor=\"white\"><tr><td bgcolor=\"black\" align=\"center\" colspan=\"2\"><font color=\"white\">val" + str(
                            node) + "</font></td></tr><tr><td align=\"left\" port=\"r1\"> " + str(com) + "</td></tr></table>>];\n")
                    # file.write("val" + str(node) + ";\n")
                    file.write("}\n")
            file.write("}\n")
        for x in depend_dict:
            vn = "val" + str(x)
            for t in depend_dict[x]:
                file.write("val" + str(t) + " -> " + vn + ";\n")
        file.write("}\n")
    if os.path.exists("graph1.svg"):
        os.remove("graph1.svg")
    os.system("dot -Tsvg vis.gv -o graph1.svg")
    return flask.render_template("visualization.html")


@app.route("/css/graphviz.svg.css", methods=['GET'])
def get_css():
    return flask.send_file("css/graphviz.svg.css")


@app.route("/js/jquery.graphviz.svg.js", methods=['GET'])
def get_js():
    return flask.send_file("js/jquery.graphviz.svg.js")


# @app.route("/var/<vid>", methods=['GET'])
# def frontend_var(vid):
#     url = ns["var/" + str(vid)]
#     his = []
#     qres = g.query(
#         """SELECT ?ts ?val_url ?com
#         WHERE {
#             ?url kg:kgplType kg:kgplVariable ;
#                kg:valueHistory ?ts .
#             ?ts kg:hasKGPLValue ?val_url ;
#                 kg:hasComment ?com .
#         }""",
#         initBindings={'url': url}
#     )

#     if len(qres) != 0:
#         for ts, val_url, com in qres:
#             his.append(str(ts))
#             print("44444444444444444444444")
#             print(his)
#             print(str(ts))
#             val_url = str(val_url)
#             ts_for_query = ts
#             ts = str(ts)
#             com = str(com)
#             # print(val_url)
#             # actual_val_id = int(val_url[val_url.rfind('/') + 1:])
#             actual_ts = float(ts[ts.rfind('/') + 1:])

#             # while True:
#             #     qres = g.query(
#             #         """SELECT ?history ?val_uri
#             #         WHERE {
#             #             ?url kg:hasComment ?com ;
#             #                  kg:hasHistory ?history ;
#             #                  kg:hasKGPLValue ?val_uri .
#             #         }""",
#             #         initBindings={'url': ts_for_query}
#             #     )
#             #     print(ts)
#             #     if len(qres) == 0:
#             #         print("end")
#             #         break
#             #     elif len(qres) != 1:
#             #         print("place two")

#             #         flask.abort(500)
#             #     for history, val_uri in qres:
#             #         ts_for_query = history
#             #         # rst.append(int(val_uri[val_uri.rfind('/') + 1:]))
#             #         his.append(history)
#         context = {
#             "KGPLVariable": str(url),
#             "Currently containing KGPLValue": val_url,
#             "Current comment": com,
#             "Last modified timestamp": actual_ts,
#             "Last modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(actual_ts)),
#             "History": his
#         }

#         return flask.jsonify(**context), 200
#     elif len(qres) == 0:
#         return flask.abort(404)
#     else:
#         return flask.abort(500)


@app.route("/var/<vid>/ts/<ts>", methods=['GET'])
def frontend_timestamp(vid, ts):
    url = ns["var/" + str(vid) + "/ts/" + str(ts)]
    # qres = g.query(
    #     """SELECT ?ts ?val_url
    #     WHERE {
    #         ?url kg:kgplType kg:kgplVariable ;
    #            kg:valueHistory ?ts .
    #         ?ts kg:hasKGPLValue ?val_url .
    #     }""",
    #     initBindings={'url': url}
    # )

    qres = g.query(
        """SELECT ?kgval
        WHERE {
            ?url kg:hasKGPLValue ?kgval.
        }""",
        initBindings={'url': url}
    )

    if len(qres) == 1:
        for kgval, in qres:
            context = {
                "KGPLVariable \""+str(url)+"\" at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(ts))),
                "timestamp": ts,
                "KGPLValue": kgval
            }
            return flask.jsonify(**context), 200
    elif len(qres) == 0:
        return flask.abort(404)
    else:
        return flask.abort(500)


def close_graph():
    g.close()
    dg.close()
    print("server is closing")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print("No file part")
            return redirect("/upload")
        file = request.files['file']
        file_id = request.files['value_id']
        # print(file_id)
        # print(type(file_id))

        # print(file_id.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            print("No selected file")
            return redirect("/upload")
        if file and allowed_file(file.filename):
            # print(type(file.filename))
            # print(file.filename)

            # print(type(add_id))
            # new_name_before = "val_"+add_id+"_" + str(file.filename)
            # print(new_name_before)
            new_name = secure_filename(
                "val_"+file_id.filename+"_"+str(file.filename))
            print("allow")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            # add a kgplvalue
            context = {
                "filename_stored": new_name
            }
            return flask.jsonify(**context), 200

    # return flask.render_template("upload.html")


@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    print(app.config['UPLOAD_FOLDER']+filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename), 200

atexit.register(close_graph)

if __name__ == '__main__':
    GDB = GraphDB("bolt://localhost:7687", "neo4j", "password")
    app.run(debug=True)
    greeter.close()
