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
    # Return (srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime)
    #
    def getIncomingSharingPairs(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (a:ObservedFile), (b:ObservedFile) "
                                  "WHERE a.file_hash = b.file_hash "
                                  "AND a.username <> b.username "
                                  "AND a.sync_time < b.sync_time "
                                  "AND b.username = $username "
                                  "RETURN a.file_name, a.username, a.sync_time, b.file_name, b.username, b.sync_time",
                                  username=username)

            for srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime in results:
                yield (srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime)

            session.close()

    #
    #
    #
    def getOutgoingSharingPairs(self, username):
        with self.driver.session() as session:
            results = session.run("MATCH (a:ObservedFile), (b:ObservedFile) "
                                  "WHERE a.file_hash = b.file_hash "
                                  "AND a.username <> b.username "
                                  "AND a.sync_time < b.sync_time "
                                  "AND a.username = $username "
                                  "RETURN a.file_name, a.username, a.sync_time, b.file_name, b.username, b.sync_time",
                                  username=username)

            for srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime in results:
                yield (srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime)

            session.close()

    #
    # For a particular user, yield a tuple of the file hash, name, size, modifiedTime, and syncTime
    #
    def getAllFiles(self, username):
        with self.driver.session() as session:
            resultPairs = session.run("MATCH (a:ObservedFile) "
                                      "WHERE a.username = $username "
                                      "RETURN a.file_hash, a.file_name, a.file_size, a.modified, a.sync_time",
                                     username = username)

            for h, fn, fs, m, st in resultPairs:
                yield (h, fn, fs, m, st)

            session.close()



    def getVersionedPairs(self, username):
        with self.driver.session() as session:
            resultPairs = session.run("MATCH (cur:ObservedFile)-[r:VersionPredecessor]->(prev:ObservedFile) "
                                     "WHERE cur.username = $username "
                                     "AND prev.username = $username "
                                      "RETURN cur.file_name, cur.file_hash, cur.file_size, cur.modified, prev.file_hash, prev.file_size, prev.modified",
                                     username = username)

            if resultPairs is None:
                return None
            else:
                # Return (fname, hash, size, lastmodified, hash, size, lastmodified)
                for fname, curH, curFS, curM, prevH, prevFS, prevM in resultPairs:
                    yield (fname, curH, curFS, curM, prevH, prevFS, prevM)

            session.close()



    def addObservations(self, observations):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_observations, observations)


    @staticmethod
    def _create_and_return_observations(tx, observations):
        for obs in observations:

            #Get version predecessor, if any
            versionPredecessor = tx.run("MATCH (a:ObservedFile) WHERE a.file_name = $file_name "
                                        "AND a.username = $username "
                                        "RETURN id(a), a.file_hash "
                                        "ORDER BY a.sync_time DESC LIMIT 1 ",
                                        file_name=obs["file_name"],
                                        username=obs["username"])

            vpNode = versionPredecessor.single()

            createResult = None
            if vpNode is None or vpNode[1] != obs["file_hash"]:
                createResult = tx.run("CREATE (a:ObservedFile) "
                                      "SET a.file_hash = $file_hash, "
                                      "a.file_name = $file_name, "
                                      "a.file_size = $file_size, "
                                      "a.username = $username, "
                                      "a.modified = $modified, "
                                      "a.sync_time = $sync_time "
                                      "RETURN id(a) ",
                                      file_hash=obs["file_hash"],
                                      file_name=obs["file_name"],
                                      file_size=obs["file_size"],
                                      username=obs["username"],
                                      modified=obs["modified"],
                                      sync_time=obs["sync_time"])

            # Get share match, if any

            # Add predecessor edge, if appropriate
            if vpNode is not None and createResult is not None:
                prevNodeId = vpNode[0]
                curNodeId = createResult.single()[0]

                edgeResult = tx.run("MATCH (cur:ObservedFile), (prev:ObservedFile) "
                                    "WHERE id(cur) = $curNodeId "
                                    "AND id(prev) = $prevNodeId "
                                    "CREATE (cur)-[r:VersionPredecessor]->(prev) "
                                    "RETURN id(r)",
                                    curNodeId=curNodeId,
                                    prevNodeId=prevNodeId)

            # Add share edge, if appropriate

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
    out += "<tr><td>Hash</td><td>Filename</td><td>Size</td><td>Last Modified</td><td>Last Sync</td><td># optional fields</td><td>Other Users</td></tr>"
    maxItems = 3
    count = 0
    for hash, fname, fsize, modified, synctime in GDB.getAllFiles(username):
        mod_date = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
        sync_date = datetime.datetime.fromtimestamp(synctime).strftime('%Y-%m-%d %H:%M:%S')

        out += "<tr><td>{}</td><td>{}</td><td>{} B</td><td>{}</td><td>{}</td><td></td><td></td></tr>".format(hash, fname, fsize, mod_date, sync_date)

        count += 1
        if count > maxItems:
            out += "<tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>"
            break
    out += "</table>"

    #
    # Identify version events
    #
    out += "<p>"
    out += "<h2>Likely version events</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Hash 1</b></td><td><b>Size 1</b></td><td><b>Last Modified 1</b></td><td><b>Hash 2</b></td><td><b>Size 2</b></td><td><b>Last Modified 2</b></td></tr>"
    for fname, h1, s1, lm1, h2, s2, lm2 in GDB.getVersionedPairs(username):
        out += "<tr><td>{}</td>".format(fname)
        out += "<td>{}</td>".format(h1)
        out += "<td>{}</td>".format(s1)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(lm1).strftime('%Y-%m-%d %H:%M:%S'))
        out += "<td>{}</td>".format(h2)
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
    out += "<tr><td><b>Source filename</b></td><td><b>Source user</b></td><td><b>Source synctime</b></td><td><b>Dst filename</b></td><td><b>Dst user</b></td><td><b>Dst synctime</b></td></tr>"
    for srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime in GDB.getOutgoingSharingPairs(username):
        out += "<tr><td>{}</td>".format(srcFname)
        out += "<td>{}</td>".format(srcUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(srcSynctime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "<td>{}</td>".format(dstFname)
        out += "<td>{}</td>".format(dstUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(dstSynctime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"

    #
    # Identify incoming sharing events
    #
    out += "<p>"
    out += "<h2>Likely incoming sharing events</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Source filename</b></td><td><b>Source user</b></td><td><b>Source synctime</b></td><td><b>Dst filename</b></td><td><b>Dst user</b></td><td><b>Dst synctime</b></td></tr>"
    for srcFname, srcUser, srcSynctime, dstFname, dstUser, dstSynctime in GDB.getIncomingSharingPairs(username):
        out += "<tr><td>{}</td>".format(srcFname)
        out += "<td>{}</td>".format(srcUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(srcSynctime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "<td>{}</td>".format(dstFname)
        out += "<td>{}</td>".format(dstUser)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(dstSynctime).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"


    return f'User {escape(username)} <br> {out}'

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

    # show the user profile for that user
    return json.dumps(username)


if __name__ == '__main__':
    GDB = GraphDB("bolt://localhost:7687", "neo4j", "password")

    app.run(debug=True, port=8889)
    greeter.close()
