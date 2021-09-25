from flask import Flask, abort, request, jsonify
from flask_cors import CORS

from markupsafe import escape

import base64
import json
import datetime
import time
import os
from pathlib import Path

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


def matching_hashes():
    d = './data'
    hashes = {}
    for (r,x,files) in os.walk(d):
        for f in files:
            if '.json' in f:
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
            if '.json' in f:
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

    out = "<table border=1 cellpadding=5>"
    out += "<tr><td>Hash</td><td>Filename</td><td>Size</td><td>Last Modified</td><td>Last Sync</td><td># optional fields</td><td>Other Users</td></tr>"
    for k, v in data['files'].items():
        other_users = list(matches[k])
        other_users.remove(username)
        mod_date = datetime.datetime.fromtimestamp(v['modified']).strftime('%Y-%m-%d %H:%M:%S')
        sync_date = datetime.datetime.fromtimestamp(v['sync_time']).strftime('%Y-%m-%d %H:%M:%S')
        optionalItems = v.get("optionalItems", {})
        
        out += "<tr><td>{}</td><td>{}</td><td>{} B</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(k, v['file_name'], v['file_size'], mod_date, sync_date, len(optionalItems), ', '.join(other_users))
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
