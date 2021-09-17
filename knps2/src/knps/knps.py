import hashlib
from pathlib import Path
import argparse
import configparser
import json
import os
import requests
import json

CFG_DIR = '.knps'
CFG_FILE = 'knps.cfg'

DB_FILE = '.knpsdb'

def hash_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def hash_file_lines(fname):
    hashes = []
    with open(fname, "rt") as f:
        for line in f:
            line = line.strip().encode()
            hashes.append(hashlib.md5(line).hexdigest())
    return hashes

def send_sync(username, file_name, file_hash, line_hashes):
    url = "http://127.0.0.1:8889/sync/{}".format(username)
    p = Path(file_name)
    info = p.stat()
    metadata = {
        'username': username,
        'file_name': file_name,
        'file_hash': file_hash,
        'line_hashes': line_hashes,
        'file_size': info.st_size,
        'modified': info.st_mtime,
    }
    files = {}
    files['metadata'] = json.dumps(metadata)

    response = requests.post(url, files=files)
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



class User:
    def __init__(self):
        self.load_db()
        self.username, self.userhash = self.get_current_user()


    def login(self, username, password):
        # This is not really a login. TODO: make this good
        self.username = username
        salt = username.encode() # BAD!
        self.userhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

        if self.username not in self.db:
            self.db[self.username] = {}

        self.db['__CURRENT_USER__'] = (self.username, self.userhash)
        self.save_db()

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

    def add_dir(self, watcher):
        if 'dirs' not in self.db[self.username]:
            self.db[self.username]['dirs'] = []

        d = watcher.dir

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

class Watcher:
    def __init__(self, user):
        self.dir = None
        self.user = user
        self.config = None

    def watch(self, directory):
        p = Path(directory)

        if not p.exists() and p.is_dir():
            raise NotADirectoryError("Cannot watch: not a directory")

        # Make sure it's an absolute path
        self.dir = p.resolve()

        cfg = self.get_cfg()

        if not cfg.exists():
            self.make_cfg()
            self.user.add_dir(self)
            print("Watching {}".format(self.dir))

        self.config = configparser.ConfigParser()
        self.config.read(self.get_cfg())

        if self.config['KNPS']['user'] != self.user.username:
            raise WrongUserError("User {} does not match owner of directory".format(self.user.username))

    def status(self):
        for path in self.dir.iterdir():
            info = path.stat()
            print(info)

    def get_cfg(self):
        return self.dir.joinpath(CFG_DIR, CFG_FILE)

    def make_cfg(self):
        cfg_dir = self.dir.joinpath(CFG_DIR)
        cfg_dir.mkdir(exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.get_cfg())
        self.config.add_section('KNPS')
        self.config.set('KNPS', 'user', self.user.username)

        self.config.write(self.get_cfg().open("w"))

    def sync_file(self, f):
        file_hash = hash_file(f)
        line_hashes = hash_file_lines(f)
        send_sync(self.user.username, f, file_hash, line_hashes)


if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description='KNPS command line')

    parser.add_argument('command', type=str, help="KNPS command")
    parser.add_argument('args', type=str, help="KNPS command arguments", nargs='*' )

    args = parser.parse_args()

    command = args.command
    command_args = args.args

    u = User()

    if command == 'login':
        u.login(command_args[0], 'password1') # TODO: BAD!
    elif command == 'watch':
        w = Watcher(u)
        w.watch(command_args[0])
    elif command == 'status':
        dirs = u.get_dirs()
        files = u.get_files()
        print("You have {} top-level directories and {} files watched by knps.".format(len(dirs), len(files)))

        if 'dirs' in command_args:
            print("\nWatched directories:")
            for d in dirs:
                print("   {}".format(d))

        if 'files' in command_args:
            print("\nWatched files:")
            for d in files:
                print("   {}".format(d))

        if len(command_args) > 0:
            print()

    elif command == 'sync':
        w = Watcher(u)
        files = u.get_files()
        for f in files:
            w.sync_file(f)
