import hashlib
from pathlib import Path
import argparse
import configparser
from datetime import datetime
import json
import os
import requests
import json
import webbrowser

CFG_DIR = '.knps'
CFG_FILE = 'knps.cfg'

DB_FILE = '.knpsdb'

###################################################
# Some util functions
###################################################
def hash_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

#
# Hash all the lines of a file. Should only be applied to a text file
#
def hash_file_lines(fname):
    hashes = []
    with open(fname, "rt") as f:
        for line in f:
            line = line.strip().encode()
            hashes.append(hashlib.md5(line).hexdigest())
    return hashes

#
# Transmit observations to the server
#
def send_synclist(username, observationList):
    url = "http://127.0.0.1:8889/synclist/{}".format(username)

    obsList = []
    for file_name, file_hash, line_hashes, optionalItems in observationList:
        p = Path(file_name)
        info = p.stat()
        metadata = {
            'username': username,
            'file_name': file_name,
            'file_hash': file_hash,
            'line_hashes': line_hashes,
            'file_size': info.st_size,
            'modified': info.st_mtime,
            'optionalItems': optionalItems
        }
        obsList.append({'metadata': metadata})

    response = requests.post(url, files={'observations': json.dumps(obsList)})
    obj_data = response.json()

    return obj_data



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


    def login(self):
        ROOTURL = "http://127.0.0.1:8889"
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


    def load_db(self):
        p = Path(Path.home(), DB_FILE)
        if p.exists():
            self.db = json.load(p.open())
        else:
            self.db = {}

    def save_db(self):
        json.dump(self.db, Path(Path.home(), DB_FILE).open('wt'), indent=2)

    def get_current_user(self):
        (u, h) = self.db.get('__CURRENT_USER__', (None, None))
        return u, h

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


    #
    # Collect some observations
    #
    def observeAndSync(self):
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
        while todoPair is not None:
            k, todoList = todoPair

            # Process what's on the TODO list, upload it a chunk at a time
            observationList = []
            todoChunk = todoList
            skipCount = 0
            uploadCount = 0
            for f in todoChunk:
                try:
                    observationList.append(self._observeFile_(f))
                    uploadCount += 1
                except:
                    skipCount += 1

            send_synclist(self.user.username, observationList)
            print("Observed and uploaded", uploadCount, "items. Skipped", skipCount)

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
    def _observeFile_(self, f):
        file_hash = hash_file(f)
        line_hashes = hash_file_lines(f)
        optionalFields = {}
        optionalFields["filetype"] = "unknown"
        return (f, file_hash, line_hashes, optionalFields)

#
# main()
#
if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description='KNPS command line')

    parser.add_argument("--login", action="store_true", help="Perform login")
    parser.add_argument("--status", nargs="*", help="Check KNPS status", default=None)
    parser.add_argument("--watch", help="Add a directory to watch")
    parser.add_argument("--sync", action="store_true", help="Sync observations to service")
    parser.add_argument('args', type=str, help="KNPS command arguments", nargs='*' )

    args = parser.parse_args()

    u = User()
    if args.login:
        u.login() # TODO: BAD!

    elif args.watch:
        w = Watcher(u)
        w.watch(args.watch)

    elif args.status is not None:
        print("You are logged in as", u.username)
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
        Watcher(u).observeAndSync()
