from flask import Flask, abort, request, jsonify
from flask_cors import CORS

from markupsafe import escape
from neo4j import GraphDatabase

import base64
import json
import datetime
import time
import os
from pathlib import Path

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
