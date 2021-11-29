import hashlib
from pathlib import Path
import argparse
import configparser
from datetime import datetime
import json
import os
import requests
import json
import csv
import pandas as pd
import PyPDF2
import re
import random
import time
import numpy as np
import webbrowser
import yaml
import subprocess
import uuid
import socket
import threading
import mimetypes
from binaryornot.check import is_binary

from settings import (
    CACHE_FILE_PROCESSING,
    KNPS_SERVER_DEV,
    KNPS_SERVER_PROD
)

CFG_DIR = '.knps'
CFG_FILE = 'knps.cfg'

DB_FILE = '.knpsdb'
DIR_DB_FILE = '.knps_dir_db'


###################################################
# Some util functions
###################################################
def get_version(file_loc = __file__):
    cwdir = os.path.dirname(os.path.realpath(file_loc))
    proj_ver = subprocess.run(["git", "describe", "--tags", "--long"], stdout=subprocess.PIPE, text=True, cwd=cwdir).stdout.strip()
    rev_count = subprocess.run(["git", "log", "--oneline"], stdout=subprocess.PIPE, text=True, cwd=cwdir).stdout.strip()
    rev_count = len(rev_count.split("\n"))
    return f'{proj_ver}-{rev_count}'


HASH_CACHE = {}
def hash_file(fname):
    if fname not in HASH_CACHE:
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        HASH_CACHE[fname] = hash_md5.hexdigest()
    return HASH_CACHE[fname]

#
# Hash all the lines of a file. Should only be applied to a text file
#
def hash_file_lines(fname, file_type):
    hashes = []
    text = ""

    if file_type == "application/pdf":
        return hash_pdf_file_lines(fname)

    if file_type == "text/csv":
        return hash_csv_file_lines(fname)

    if not is_binary(fname):
        with open(fname, "rt") as f:
            for line in f:
                text = text + " " + line
                line = line.strip().encode()
                hashes.append(hashlib.md5(line).hexdigest())

    return hashes

def getShinglesFname(fname, file_type):
    text = ""
    if file_type != "text/csv":
        with open(fname, "rt") as f:
            for line in f:
                text = text + " " + line
    return getShingles(text, fname, file_type)

def hash_csv_file_lines(fname):
    data = pd.read_csv(fname)
    hashes = []
    for i in range(100):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i]
        hashes.append(hashlib.md5(row.__str__().strip().encode()).hexdigest())
    for i in range(100, 1000, 5):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i:(i+10)]
        hashes.append(hashlib.md5(row.__str__().strip().encode()).hexdigest())
    for i in range(1000, 10000, 50):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i:(i+100)]
        hashes.append(hashlib.md5(row.__str__().strip().encode()).hexdigest())
    diff = data.shape[0] - 10000
    jump = diff//100
    for i in range(10000, data.shape[0], jump):
        row = data.iloc[i:(i+jump)]
        hashes.append(hashlib.md5(row.__str__().strip().encode()).hexdigest())

    return hashes

## This is very slow
## near-miss detection (hash-shingling)
def hash_pdf_file_lines(fname):
    hashes = []
    pdfFileObj = open(fname, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
    for pageNumber in range(pdfReader.getNumPages()):
        pageObj = pdfReader.getPage(pageNumber)
        # hashes.append(hashlib.md5(pageObj.extractText().strip().encode()).hexdigest())
        lines = pageObj.extractText().splitlines()
        for line in lines:
            line = line.strip().encode()
            hashes.append(hashlib.md5(line).hexdigest())
    pdfFileObj.close()
    return hashes

# def send_synclist_thread(user, observationList, comment=None):
def observeAndSyncThread(user, file_loc):
    user.observeAndSync(file_loc)

#
# Transmit observations to the server
#
def send_synclist(user, observationList, file_loc, comment=None):
    knps_version = get_version(file_loc)
    install_id = user.get_install_id()
    hostname = socket.gethostname()
    print("KNPS Version: ", knps_version)

    url = "{}/synclist/{}".format(user.get_server_url(), user.username)

    login = {
        'username': user.username,
        'access_token': user.access_token
    }

    obsList = []
    for file_name, file_hash, file_type, line_hashes, optionalItems in observationList:
        p = Path(file_name)
        info = p.stat()

        metadata = {
            'username': user.username,
            'file_name': file_name,
            'file_hash': file_hash,
            'filetype': file_type,
            'line_hashes': line_hashes,
            'file_size': info.st_size,
            'modified': info.st_mtime,
            'knps_version': knps_version,
            'install_id': install_id,
            'hostname': hostname,
            'optionalItems': optionalItems
        }
        obsList.append({'metadata': metadata})

    fDict = {'observations': json.dumps(obsList)}
    response = requests.post(url, files=fDict, data=login)
    obj_data = response.json()

    return obj_data

#
# Transmit observations to the server
#
def send_adornment(user, filename, comment):
    url = "{}/adorn/{}".format(KNPS_SERVER_URL, user.username)

    login = {
        'username': user.username,
        'access_token': user.access_token
    }

    fDict = {'filename': json.dumps(filename), 'comment': json.dumps(comment)}
    response = requests.post(url, files=fDict, data=login)
    obj_data = response.json()

    return obj_data


#
# Transmit observations to the server
#
def send_createdataset(user, id, title, desc, targetHash):
    url = "{}/createdataset/{}".format(KNPS_SERVER_URL, user.username)

    login = {
        'username': user.username,
        'access_token': user.access_token
    }

    fDict = {'id': json.dumps(id), 'title': json.dumps(title), 'desc': json.dumps(desc), 'targetHash': json.dumps(targetHash)}
    response = requests.post(url, files=fDict, data=login)
    obj_data = response.json()

    return obj_data

def hash_CSV_columns(fname):
    hashes = []
    df = pd.read_csv(fname)
    for column_name in df.columns:
        column = df[column_name].__str__().strip().encode()
        hashes.append(hashlib.md5(column).hexdigest())
    return hashes

def hash_image(fname):
    #Have this take in and hash an image through thing described earlier.
    return None

def get_csv_file_shingles(fname, fingerprint_bytes):
    data = pd.read_csv(fname)
    hashes = []
    for i in range(100):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i]
        hashes.append(int.from_bytes(hashlib.sha256(row.__str__().encode()).digest()[:fingerprint_bytes], 'little'))
    for i in range(100, 1000, 5):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i:(i+10)]
        hashes.append(int.from_bytes(hashlib.sha256(row.__str__().encode()).digest()[:fingerprint_bytes], 'little'))
    for i in range(1000, 10000, 50):
        if i >= data.shape[0]:
            return hashes;
        row = data.iloc[i:(i+100)]
        hashes.append(int.from_bytes(hashlib.sha256(row.__str__().encode()).digest()[:fingerprint_bytes], 'little'))
    diff = data.shape[0] - 10000
    jump = diff//100
    for i in range(10000, data.shape[0], jump):
        row = data.iloc[i:(i+jump)]
        hashes.append(int.from_bytes(hashlib.sha256(row.__str__().encode()).digest()[:fingerprint_bytes], 'little'))
    return hashes

# This fucntion removes punctiation and whitespace.
# The returns a list of tokens(words) and should not contain any lists or anything along those lines.
def createShingleFingerprints(s, fname, file_type, shingle_length = 5, fingerprint_bytes = 8):
    if file_type == "text/csv":
        return get_csv_file_shingles(fname, fingerprint_bytes)
    s = re.sub(r'[^\w\s]', '', s)
    words = s.lower().split()
    shingles = []
    if len(words) <= shingle_length:
        fingerprint = int.from_bytes(hashlib.sha256(words.__str__().encode()).digest()[:fingerprint_bytes], 'little')
        return {fingerprint}
    for i in range(len(words)-shingle_length):
        fingerprint = int.from_bytes(hashlib.sha256(words[i:i+shingle_length].__str__().encode()).digest()[:fingerprint_bytes], 'little')
        shingles.append(fingerprint)
    return shingles

## So for each s
## This function should find shingles.
def getShingles(s, fname, file_type, shingle_length = 5, num_shingles = 10, fingerprint_bytes = 8):
    random.seed(0)
    shingles = []
    all_shingles = createShingleFingerprints(s, fname, file_type, shingle_length, fingerprint_bytes)
    for i in range(num_shingles):
        factor = int(random.random()*(256**fingerprint_bytes))
        shift = int(random.random()*(256**fingerprint_bytes))
        new_shingles = {}
        for shingle in all_shingles:
            new_shingles[(factor*shingle+shift)%(256**fingerprint_bytes)] = shingle
        minimum = min(new_shingles.keys())
        shingles.append(str(new_shingles[minimum]))
    return shingles

## use the mimetype
def get_file_type(f):
    type, encoding = mimetypes.guess_type(f)

    if type:
        return type
    elif is_binary(f):
        return 'binary/unknown'
    else:
        return 'text/unknown'


## check if the file is binary by trying to open it


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class WrongUserError(Error):
    """Exception raised for errors when the wrong users tries to update KNPS.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

#
# Represents, um, a User.
#
class User:
    def __init__(self):
        self.load_db()
        self.username, self.access_token = self.get_current_user()

    def login(self, username=None):
        # FOR TEMP LOGIN.
        if username:
            self.username = username
            self.access_token = "INSECURE_TOKEN_{}".format(username)
            if self.username not in self.db:
                self.db[self.username] = {}

            self.db['__CURRENT_USER__'] = (self.username, self.access_token)
            self.save_db()
            print("You are now logged in as: {}".format(username))

        else:
            ROOTURL = self.get_server_url()
            url = ROOTURL + "/cli_login"

            response = requests.get(url)
            data = response.json()

            if 'login_url' in data:
                print("Opening web browser for login...")
                webbrowser.open(data['login_url'])
                token_url = ROOTURL + "/get_token"
                token_response = requests.post(token_url, data={'login_code': data['login_code']})
                token_data = token_response.json()

                username = token_data['email']
                # This is not really a login. TODO: make this good
                self.username = username
                self.access_token = token_data['access_token']

                if self.username not in self.db:
                    self.db[self.username] = {}

                self.db['__CURRENT_USER__'] = (self.username, self.access_token)
                self.save_db()

                print("You are now logged in as: {}".format(token_data['email']))

    def logout(self):
        ROOTURL = self.get_server_url()
        url = ROOTURL + "/cli_logout"

        response = requests.post(url, data={'access_token': self.access_token})
        data = response.json()

        if 'logout_url' in data:
            del(self.db['__CURRENT_USER__'])
            self.username = None
            self.access_token = None
            self.save_db()

            print("Opening web browser for logout...")
            webbrowser.open('https://dev-66403161.okta.com/login/signout')

    def load_db(self):
        p = Path(Path.home(), DB_FILE)
        print(p)
        if p.exists():
            self.db = json.load(p.open())
        else:
            self.db = {}

    def save_db(self):
        json.dump(self.db, Path(Path.home(), DB_FILE).open('wt'), indent=2)

    def get_current_user(self):
        (u, h) = self.db.get('__CURRENT_USER__', (None, None))
        return u, h

    def set_server(self, url):
        # TODO: do some validation here
        self.db['__SERVER__'] = url
        self.save_db()

    def get_server(self):
        return self.db.get('__SERVER__', 'dev')

    def get_server_url(self):
        url = self.get_server()

        if url == 'prod':
            url = KNPS_SERVER_PROD
        elif url == 'dev':
            url = KNPS_SERVER_DEV

        return 'http://{}'.format(url)

    def get_install_id(self):
        if not self.db:
            self.load_db()

        if '__INSTALL_ID__' not in self.db:
            self.db['__INSTALL_ID__'] = str(uuid.uuid1())
            self.save_db()

        return self.db['__INSTALL_ID__']

    def add_dir(self, d):
        if 'dirs' not in self.db[self.username]:
            self.db[self.username]['dirs'] = []

        if d not in self.db[self.username]['dirs']:
            self.db[self.username]['dirs'].append(str(d))
            self.save_db()

    def get_dirs(self):
        return self.db[self.username].get('dirs', [])

    def get_files(self):
        files = []
        for d in self.get_dirs():
            files += [os.path.join(r, file) for r,d,f in os.walk(d) if '.knps' not in r for file in f]

        return files

    def getNextTodoList(self):
        todoDict = self.db[self.username].get("todos", {})
        if len(todoDict) == 0:
            return None
        for k, v in todoDict.items():
            return (k, v)

    def removeTodoList(self, todoKey):
        todoDict = self.db[self.username].get("todos", {})
        todoDict.pop(todoKey, None)
        self.save_db()

    def addTodoList(self, todoList):
        todoDict = self.db[self.username].setdefault("todos", {})
        todoDict[datetime.now().microsecond] = todoList
        self.save_db()

#
# This maintains a user's set of watched files and dirs
#
class Watcher:
    def __init__(self, user):
        self.user = user
        self.config = None
        self.db = None
        self.knps_version = get_version()

    #
    # Add something to the watchlist
    #
    def watch(self, directory):
        p = Path(directory)

        if not p.exists() and p.is_dir():
            raise NotADirectoryError("Cannot watch: not a directory")

        # Make sure it's an absolute path
        dir = p.resolve()
        cfg = self.__get_cfg__(dir)
        # The target shouldn't already have a .knps config dir
        if cfg.exists():
            self.config = configparser.ConfigParser()
            self.config.read(self.__get_cfg__(dir))

            if self.config['KNPS']['user'] == self.user.username:
                raise Error("You're already watching that directory")
            else:
                raise WrongUserError("You can't watch that directory. User '{}' is already watching it (But you're '{}'.)".format(self.config['KNPS']['user'], self.user.username))


        # The target dir doesn't seem to be watched, so go ahead!
        self.__make_cfg__(dir)
        self.user.add_dir(dir)
        print("Watching {}".format(dir))


    def __get_cfg__(self, d):
        return d.joinpath(CFG_DIR, CFG_FILE)

    def __make_cfg__(self, d):
        cfg_dir = d.joinpath(CFG_DIR)
        cfg_dir.mkdir(exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.__get_cfg__(d))
        self.config.add_section('KNPS')
        self.config.set('KNPS', 'user', self.user.username)

        self.config.write(self.__get_cfg__(d).open("w"))

    def __load_local_db__(self):
        p = Path(Path.home(), DIR_DB_FILE)
        db_version = None
        if p.exists():
            try:
                self.db = json.load(p.open())
                db_version = self.db.get('__KNPS_VERSION__', None)
            except Exception as e:
                print(e)
                pass

        if not self.db or db_version != self.knps_version:
            self.db = {'__KNPS_VERSION__': self.knps_version}

        if self.user.username not in self.db:
            self.db[self.user.username] = {}

        if self.user.get_server() not in self.db[self.user.username]:
            self.db[self.user.username][self.user.get_server()] = {}

    def __save_local_db__(self):
        json.dump(self.db, Path(Path.home(), DIR_DB_FILE).open('wt'), indent=2)

    def file_already_processed(self, f):
        if not CACHE_FILE_PROCESSING:
            return False

        if not self.db:
            self.__load_local_db__()

        file_hash = hash_file(f)

        return file_hash in self.db[self.user.username][self.user.get_server()] and f in self.db[self.user.username][self.user.get_server()][file_hash]

    def record_file_processing(self, f):
        if CACHE_FILE_PROCESSING:
            if not self.db:
                self.__load_local_db__()

            file_hash = hash_file(f)
            if file_hash not in self.db:
                self.db[self.user.username][self.user.get_server()][file_hash] = {}
            self.db[self.user.username][self.user.get_server()][file_hash][f] = 1

    #
    # Comment on an observed file
    #
    def addComment(self, f, comment):
        # Must clear the observation sync list first
        self.observeAndSync()

        # Transmit observation and comment
        send_adornment(self.user, str(Path(f).resolve()), comment)

    #
    # Create a Dataset for a given file.
    #
    def addDataset(self, configYamlFile):
        #self.observeAndSync()

        with open(configYamlFile, "r") as stream:
            configYaml = yaml.safe_load(stream)

            send_createdataset(self.user, configYaml["id"], configYaml["title"], configYaml["desc"], configYaml["targetHash"])

    #
    # Collect some observations
    #
    def observeAndSync(self, file_loc = None):
        if file_loc == None:
            file_loc = __file__
        # If there are TODO items outstanding, great.
        todoPair = self.user.getNextTodoList()

        #
        # If not, then we need to generate a TODO list and add it
        # The lists should be up to K items long. That lets us
        # make incremental progress in case the program gets
        # interrupted.
        #
        if todoPair is None:
            print("No existing observation list. Formulating new one...")
            k = 50

            longTodoList = [x for x in self.user.get_files()]
            smallTodoLists = [longTodoList[i:i+k] for i in range(0, len(longTodoList), k)]

            for smallTodoList in smallTodoLists:
                self.user.addTodoList(smallTodoList)
            todoPair = self.user.getNextTodoList()

        print("Processing observation list...")

        #
        # Now finish all outstanding TODO lists. Mark them
        # as done as we go.
        #
        self.__load_local_db__()
        while todoPair is not None:
            k, todoList = todoPair

            # Process what's on the TODO list, upload it a chunk at a time
            observationList = []
            todoChunk = todoList
            skipCount = 0
            uploadCount = 0
            for f in todoChunk:
                print("Processing", f)

                if self.file_already_processed(f):
                    print(" -- Already processed")
                    continue

                try:
                    observationList.append(self._observeFile_(f))
                    uploadCount += 1
                    self.record_file_processing(f)
                except Exception as e:
                    print("*** Skipping: {}".format(e))
                    skipCount += 1
            print("Sending the synclist")
            response = send_synclist(self.user, observationList, file_loc)
            if 'error' in response:
                print('ERROR: {}'.format(response['error']))
                break
            else:
                print("Observed and uploaded", uploadCount, "items. Skipped", skipCount)
                self.__save_local_db__()

                # Mark the TODO list as done
                self.user.removeTodoList(k)

                # Get the next one if available
                todoPair = self.user.getNextTodoList()

    #
    # This is where we collect observation data.
    #
    # The input is a file path.
    #
    # The output is a tuple with 4 elements:
    # 1) The username
    # 2) The file path
    # 3) The file hash
    # 4) Line hashes
    # 5) A dictionary of optional objects. This can vary according to
    #    the file type or whatever we like. IF YOU ARE ADDING NEW INFO
    #    DURING THE PROFILE STAGE, ADD IT TO THIS DICTIONARY!
    #
    ### TODO:
    ### more ways to do partial hashes (based upon file type)

    def _observeFile_(self, f):
        file_hash = hash_file(f)
        file_type = get_file_type(f)
        line_hashes = hash_file_lines(f, file_type)
        optionalFields = {}
        optionalFields["filetype"] = file_type
        ##CSV_Column_hashs
        # if "csv" in file_type:
        #     column_hashes = hash_CSV_columns(f)
        #     optionalFields["column_hashes"] = column_hashes

        # if file_type.startswith("text/") and file_type != "text/csv":
        if file_type.startswith("text/"):
            shingles = getShinglesFname(f, file_type)
            optionalFields["shingles"] = shingles
        return (f, file_hash, file_type, line_hashes, optionalFields)

#
# main()
#
if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description='KNPS command line')

    parser.add_argument("--login", action="store_true", help="Perform login")
    parser.add_argument("--login_temp", help="Temporary dev login bypass. INSECURE!")
    parser.add_argument("--logout", action="store_true", help="Logout current user")
    parser.add_argument("--status", nargs="*", help="Check KNPS status", default=None)
    parser.add_argument("--watch", help="Add a directory to watch")
    parser.add_argument("--comment", nargs="+", help="Add a comment to a data object")
    parser.add_argument("--addDataset", help="Add a Dataset to the graph. Takes a YAML file")
    parser.add_argument("--sync", action="store_true", help="Sync observations to service")
    parser.add_argument("--server", help="Set KNPS server. Options: dev, prod, or address:port")
    parser.add_argument("--version", action="store_true", help="Display version information")
    parser.add_argument('args', type=str, help="KNPS command arguments", nargs='*' )

    args = parser.parse_args()

    u = User()
    if args.login:
        u.login()
    elif args.login_temp:
        # TODO: remove this. this is a temporary login bypass for dev purposes
        u.login(args.login_temp)
    elif args.logout:
        u.logout()
    elif args.watch:
        if not u.username:
            print("Not logged in.")
        else:
            w = Watcher(u)
            w.watch(args.watch)

    elif args.comment:
        if not u.username:
            print("Not logged in.")
        else:
            if len(args.comment) < 2:
                print("Provide the target filename and at least a 1-word comment")
                sys.exit(0)

            w = Watcher(u)
            w.addComment(args.comment[0], " ".join(args.comment[1:]))

    elif args.addDataset:
        if not u.username:
            print("Not logged in")
        else:
            w = Watcher(u)
            w.addDataset(args.addDataset)

    elif args.status is not None:
        print("KNPS Version: ", get_version())
        if not u.username:
            print("Not logged in; please run: knps --login")
        else:
            print("User: {}    Server: {}".format(u.username, u.get_server()))
            print()
            dirs = u.get_dirs()
            files = u.get_files()
            print("You have {} top-level directories and {} files watched by knps.".format(len(dirs), len(files)))

            if 'dirs' in args.status:
                print("\nWatched directories:")
                for d in dirs:
                    print("   {}".format(d))

            if 'files' in args.status:
                print("\nWatched files:")
                for d in files:
                    print("   {}".format(d))

        if 'dirs' in args.status or 'files' in args.status:
            print()

    elif args.sync:
        print("KNPS Version: ", get_version())
        if not u.username:
            print("Not logged in.")
        else:
            Watcher(u).observeAndSync()
            # thread = threading.Thread(target = observeAndSyncThread, args = (Watcher(u), __file__))
            # thread.start()


    elif args.server:
        print("Setting KNPS server to: {}".format(args.server))
        u.set_server(args.server)

    elif args.version:
        print(f'KNPS Version: {get_version()}')
