from flask import Flask, abort, request, jsonify
from flask_cors import CORS

from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from okta_helpers import is_access_token_valid, is_id_token_valid, config
from user import User

from markupsafe import escape
from neo4j import GraphDatabase

import base64
import json
import datetime
import time
import os
from pathlib import Path
import requests
import uuid

GDB = None

#
# Flask metastuff
#
app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.config.update({'SECRET_KEY': 'SomethingNotEntirelySecret'})

login_manager = LoginManager()
login_manager.init_app(app)

APP_STATE = 'ApplicationStateKNPS'
NONCE = 'SampleNonceKNPS'

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



if __name__ == '__main__':
    NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
    KNPS_SERVER = os.getenv('KNPS_SERVER', 'localhost')
    print(NEO4J_HOST, KNPS_SERVER)
    GDB = GraphDB("bolt://{}:7687".format(NEO4J_HOST), "neo4j", "password")

    app.run(debug=True, host=KNPS_SERVER, port=8889)
