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

import base64
import json
import datetime
import time
import os
from pathlib import Path
import requests
import uuid

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

def matching_hashes():
    d = './data'
    hashes = {}
    for (r,x,files) in os.walk(d):
        for f in files:
            if '.json' in f and 'login_info' not in f:
                max_time = 0
                with open(d + '/' + f, 'rt') as fin:
                    user = f.replace('.json','')
                    data = json.load(fin)
                    for k, v in data['files'].items():
                        if k not in hashes:
                            hashes[k] = []

                        hashes[k].append(user)

    return hashes



#
# Show a list of users and their high-level stats
#
@app.route("/")
def hello():
    d = './data'
    users = {}
    for (r,x,files) in os.walk(d):
        for f in files:
            if '.json' in f and 'login_info' not in f:
                max_time = 0
                with open(d + '/' + f, 'rt') as fin:
                    data = json.load(fin)
                    for k, v in data['files'].items():
                        if v['sync_time'] > max_time:
                            max_time = v['sync_time']

                users[f.replace('.json','')] = {'last_sync': max_time, 'file_count': len(data['files'])}


    file_count = '2'
    sync_date = 'adsf'
    out = "<table border=1 cellpadding=5>"
    out += "<tr><td>Name</td><td># Files</td><td>Last Sync</td></tr>"
    for u, v in users.items():
        sync_date = datetime.datetime.fromtimestamp(v['last_sync']).strftime('%Y-%m-%d %H:%M:%S')
        out += "<tr><td><a href='/user/{}'>{}</a></td><td>{}</td><td>{}</td></tr>".format(u, u, v['file_count'], sync_date)
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
            return json.dumps(data[login_code])

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

    with open(data_file, 'wt') as f:
        json.dump(data, f, indent=2)

    return redirect(url_for("logged_in"))


def find_versioned_pairs(username, data):
    seenPaths = {}
    versionSets = set()

    # Find path duplicates for this user
    for k, v in data["files"].items():
        fname = v['file_name']
        if fname in seenPaths:
            versionSets.add(fname)

        seenPaths.setdefault(fname, []).append(k)

    # Create version pairs for any observed path duplicates
    allVersionedPairs = []

    for path in versionSets:
        rawVersions = seenPaths[path]
        allVersions = [(x, data["files"].get(x).get("file_size"), data["files"].get(x).get("modified")) for x in rawVersions]
        allVersions.sort(key = lambda x: x[2])

        for i in range(1, len(allVersions)):
            v1 = allVersions[i-1]
            v2 = allVersions[i]

            # We need a 7-tuple:
            # 1) Path
            # 2) File 1 hash
            # 3) File 1 size
            # 4) File 1 modified date
            # 2) File 2 hash
            # 3) File 2 size
            # 4) File 2 modified date
            pair = (path, v1[0], v1[1], v1[2], v2[0], v2[1], v2[2])
            allVersionedPairs.append(pair)

    return allVersionedPairs



#
# Show all the details for a particular user's files
#
@app.route('/user/<username>')
def show_user_profile(username):
    matches = matching_hashes()

    # show the user profile for that user
    data_file = 'data/{}.json'.format(username)
    with open(data_file, 'rt') as f:
        data = json.load(f)

    out = "<h2>All files</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td>Hash</td><td>Filename</td><td>Size</td><td>Last Modified</td><td>Last Sync</td><td># optional fields</td><td>Other Users</td></tr>"
    for k, v in data['files'].items():
        other_users = list(matches[k])
        other_users.remove(username)
        mod_date = datetime.datetime.fromtimestamp(v['modified']).strftime('%Y-%m-%d %H:%M:%S')
        sync_date = datetime.datetime.fromtimestamp(v['sync_time']).strftime('%Y-%m-%d %H:%M:%S')
        optionalItems = v.get("optionalItems", {})

        out += "<tr><td>{}</td><td>{}</td><td>{} B</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(k, v['file_name'], v['file_size'], mod_date, sync_date, len(optionalItems), ', '.join(other_users))
    out += "</table>"

    out += "<p>"
    out += "<h2>Likely version events</h2>"
    out += "<table border=1 cellpadding=5>"
    out += "<tr><td><b>Filename</b></td><td><b>Hash 1</b></td><td><b>Size 1</b></td><td><b>Last Modified 1</b></td><td><b>Hash 2</b></td><td><b>Size 2</b></td><td><b>Last Modified 2</b></td></tr>"
    for fname, h1, s1, lm1, h2, s2, lm2 in find_versioned_pairs(username, data):
        out += "<tr><td>{}</td>".format(fname)
        out += "<td>{}</td>".format(h1)
        out += "<td>{}</td>".format(s1)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(lm1).strftime('%Y-%m-%d %H:%M:%S'))
        out += "<td>{}</td>".format(h2)
        out += "<td>{}</td>".format(s2)
        out += "<td>{}</td>".format(datetime.datetime.fromtimestamp(lm2).strftime('%Y-%m-%d %H:%M:%S'))
        out += "</tr>"
    out += "</table>"

    return f'User {escape(username)} <br> {out}'

#
# Accept an upload of a set of file observations
#
@app.route('/synclist/<username>', methods=['POST'])
def sync_filelist(username):
    data_file = 'data/{}.json'.format(username)
    p = Path(data_file)
    if p.exists():
        with open(data_file, 'rt') as f:
            data = json.load(f)
    else:
        data = {}

    if 'files' not in data:
        data['files'] = {}


    observations = json.load(request.files['observations'])
    for obs in observations:
        metadata = obs["metadata"]

        data['files'][metadata['file_hash']] = {
            'file_name': metadata['file_name'],
            'file_size': metadata['file_size'],
            'line_hashes': metadata['line_hashes'],
            'modified': metadata['modified'],
            'optionalItems': metadata['optionalItems'],
            'sync_time': time.time()
        }


    with open(data_file, 'wt') as f:
        json.dump(data, f, indent=2)

    # show the user profile for that user
    return json.dumps(username)



if __name__ == '__main__':
    app.run(debug=True, port=8889)
