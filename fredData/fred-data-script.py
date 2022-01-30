
from full_fred.fred import Fred
import os
import pandas as pd
import time
import pickle
import json
import boto3
import sys
sys.path.insert(1, os.path.abspath("../cli/src/knps"))
from knps import hash_file, hash_file_lines, get_file_type, getShinglesFname, get_version
from settings import KNPS_SERVER_PROD, KNPS_SERVER_DEV 
from io import StringIO
import argparse
from pathlib import Path
import socket 
import requests


NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
NEO4J_PORT = int(os.getenv('NEO4J_PORT', '7687'))

key_file = open('api_key.txt', 'r')
API_KEY = key_file.readline()
key_file.close()
SERIES_PICKLE_FILE = "series_ids.pickle"
os.environ['FRED_API_KEY'] = API_KEY.strip()
fred = Fred()

aws_credentials = open("aws_keys.json", 'r')
aws_keys = json.load(aws_credentials)
ACCESS_KEY_ID = aws_keys['access_key_id']
SECRET_ACCESS_KEY = aws_keys['secret_access_key']
aws_credentials.close()
os.environ["AWS_DEFAULT_REGION"] = 'us-east-1'
os.environ["AWS_ACCESS_KEY_ID"] = ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = SECRET_ACCESS_KEY
BUCKET_NAME = 'knps-data'
s3 = boto3.resource('s3')
S3_SERIES_FOLDER = 'FRED'
S3_METADATA_FOLDER = 'FRED-METADATA'
# s3_client = boto3.client('s3')
SERIES_METADATA_KEY = 'seriess'


OUTPUT_FOLDER = 'output'
LAST_PROCESSED_INDEX_FILE = 'last_processed_index.json'
LAST_PROCESSED_AWS_INDEX_FILE = 'last_processed_aws_index.json'
LAST_PROCESSED_DOWNLOAD_FILE = 'last_processed_download.json'
LAST_PROCESSED_METADATA_INDEX_FILE = 'last_processed_metadata_index.json'
FRED_URL_PREFIX_PATH = 'https://fred.stlouisfed.org/series'

def get_series_ids():
    # get all the ids of the series we want to scrape ultimately 
    categories = fred.get_child_categories(0)
    top_level_category_ids = [(cat['id'], cat['name']) for cat in categories['categories']]
    category_queue = top_level_category_ids[:]
    series_ids = set()
    # this is to respect the api rate limit
    batch_size = 21
    count = 0
    while category_queue:
        new_category_queue = []
        for category_id, _ in category_queue:
            children_categories = fred.get_child_categories(category_id)
            series_metadata = fred.get_series_in_a_category(category_id)
            if (children_categories['categories']):
                new_category_queue.extend([(cat['id'], cat['name']) for cat in children_categories['categories']])
            if (series_metadata['seriess']):
                for series in series_metadata['seriess']:
                    series_ids.add((series['id'], series['title']))
            count += 1
            if (count % batch_size) == 0:
                print("taking a nap!")
                time.sleep(60) 
        category_queue = new_category_queue

    with open(SERIES_PICKLE_FILE, 'wb') as f:
        pickle.dump(list(series_ids), f)
    print("done")

# upload csv of series to s3 bucket
def upload_series_to_s3():
    # upload csvs to aws s3 bucket
    starting_point = get_starting_point(LAST_PROCESSED_INDEX_FILE)
    # respect API rate limits
    batch_size = 120
    with open(SERIES_PICKLE_FILE, 'rb') as f:
        series_ids = pickle.load(f)
    print("{}/{} index start series scrape {}".format(starting_point+1, len(series_ids), starting_point))
    for i, (series_id, series_title) in enumerate(series_ids[starting_point:]):
        try:
            series_df = fred.get_series_df(series_id)
            csv_name = "FRED/{title}.csv".format(title=series_title)
            csv_buffer = StringIO()
            series_df.to_csv(csv_buffer)
            s3.Object(BUCKET_NAME, csv_name).put(Body=csv_buffer.getvalue())
            if (i+1)%batch_size == 0:
                print('nap time!')
                time.sleep(60)
        # if I want to stop, this will let me know where the program needs to pick up again
        except KeyboardInterrupt:
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_INDEX_FILE)
            break
        # handle any other exception, namely API limit reached 
        except:
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_INDEX_FILE)
            break
    print('done {}/{} index : {}'.format(i+starting_point+1, len(series_ids), i+starting_point))

# upload series metadata to s3 bucket
def upload_series_metadata_to_s3():
    with open(LAST_PROCESSED_INDEX_FILE, 'r') as epi:
        ending_point = json.load(epi)['index']
    starting_point = get_starting_point(LAST_PROCESSED_METADATA_INDEX_FILE)     
    # respect API rate limits
    batch_size = 120
    with open(SERIES_PICKLE_FILE, 'rb') as f:
        series_ids = pickle.load(f)
    print("{}/{} index start metadata scrape {}".format(starting_point+1, len(series_ids), starting_point))
    for i, (series_id, series_title) in enumerate(series_ids[starting_point:]):
        try:
            series_metadata = fred.get_a_series(series_id)
            series_url = "{}/{}".format(FRED_URL_PREFIX_PATH, series_id)
            series_metadata.setdefault('url', series_url)
            s3_key = "FRED-METADATA/{}.json".format(series_title)
            s3_body = json.dumps(series_metadata)
            s3.Object(BUCKET_NAME, s3_key).put(Body=s3_body)
            if (i+1)%batch_size == 0:
                print('nap time!')
                time.sleep(60)
            if (i+starting_point) == ending_point:
                print("We caught up")
                break
        # if I want to stop, this will let me know where the program needs to pick up again
        except KeyboardInterrupt:
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_METADATA_INDEX_FILE)
            break
        # handle any other exception, namely API limit reached 
        except Exception as e:
            print(repr(e))
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_METADATA_INDEX_FILE)
            break
    print('done {}/{} index : {}'.format(i+starting_point+1, len(series_ids), i+starting_point))

def save_last_good_query_index(index, file_name):
    with open(file_name, 'w') as lpi:
        json.dump({"index": index}, lpi)

def get_starting_point(index_file):
    starting_point = 0
    if os.path.isfile(index_file):
        with open(index_file, 'r') as lpi:
            starting_point = json.load(lpi)['index']
    return starting_point

#mimics the same class as seen in knps.py but adapated specifically for this script
class User:
    def __init__(self, username):
        self.username = username
        self.access_token = "INSECURE_TOKEN_{}".format(username)
        self.server_url = 'http://localhost:5000'
        # this string was obtained by running str(uuid.uuid1()) 
        self.install_id = '4cc0ee7a-814c-11ec-bd6c-aa665a53822f'

# this file is directly imported from knps.py
def observeFile(f):
    file_hash = hash_file(f)
    file_type = get_file_type(f)
    line_hashes = hash_file_lines(f, file_type)
    optionalFields = {}
    optionalFields["filetype"] = file_type
    if file_type.startswith("text/"):
        shingles = getShinglesFname(f, file_type)
        optionalFields["shingles"] = shingles
    return (f, file_hash, file_type, line_hashes, optionalFields)

# This is the same exact code as the identically named function in knps.py, just modified so it works with the scripts purposes better
def send_synclist(user, observationList, file_loc=os.path.abspath('../cli/src/knps/knps.py')):
    knps_version = get_version(file_loc)
    install_id = user.install_id
    hostname = socket.gethostname()
    print("KNPS Version: ", knps_version)

    url = "{}/synclist/{}".format(user.server_url, user.username)

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

def get_metadata_comment(f):
    with open(f, 'rb') as metadata:
        content = json.load(metadata)
    ret = 'Series Url: {}\n'.format(content['url'])
    for series_info_dict in content[SERIES_METADATA_KEY]:
        title = series_info_dict['title']
        ret += 'Series Title: {}\n'.format(title)
        for k, v in series_info_dict.items():
            if k == 'title':
                continue
            ret += '\t{}: {}\n'.format(k, v)
    ret.rstrip()
    return ret

def download_from_s3(bucket, series_title):
    try:
        csv_out_path = "{}/{}.csv".format(OUTPUT_FOLDER, series_title)
        json_out_path = "{}/{}.json".format(OUTPUT_FOLDER, series_title)
        bucket.download_file("{}/{}.csv".format(S3_SERIES_FOLDER, series_title), csv_out_path)
        bucket.download_file("{}/{}.json".format(S3_METADATA_FOLDER, series_title), json_out_path)
        return csv_out_path, json_out_path
    except Exception as e:
        print(repr(e))
        return False

def send_commentlist(user, uuids, comments):
    login = {
        'username': user.username,
        'access_token': user.access_token
    }
    url = "{}/commentlist/{}".format(user.server_url, user.username)
    commentList = [[uuids[i], comments[i]] for i in range(len(comments))]
    fDict = {'comments': json.dumps(commentList)}
    response = requests.post(url, files=fDict, data=login)
    obj_data = response.json()
    return obj_data 

def send_filenamelist(user, filenameList):
    login = {
    'username': user.username,
    'access_token': user.access_token
    }
    url = "{}/createDatasetFromFileName/{}".format(user.server_url, user.username)
    fDict = {'filenames': json.dumps(filenameList)}  
    response = requests.post(url, files=fDict, data=login)
    obj_data = response.json()
    return obj_data['uuids'] 

def download_series_from_s3(username):
    if not os.path.isdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    with open(LAST_PROCESSED_INDEX_FILE, 'r') as epi:
        ending_point = json.load(epi)['index']
    
    user = User(username)
    bucket = s3.Bucket(BUCKET_NAME)
    starting_point = get_starting_point(LAST_PROCESSED_AWS_INDEX_FILE)
    batch_size = 10

    with open(SERIES_PICKLE_FILE, 'rb') as f:
        series_ids = pickle.load(f)

    print("{}/{} index start {}".format(starting_point+1, len(series_ids), starting_point))
    
    current_batch = []
    for i, (_, series_title) in enumerate(series_ids[starting_point:]):
        try:
            download_res = download_from_s3(bucket, series_title)
            if not download_res:
                continue
            csv_out_path, json_out_path = os.path.abspath(download_res[0]), os.path.abspath(download_res[1])
            current_batch.append((csv_out_path, json_out_path)) 
            if len(current_batch) == batch_size:
                file_observations = []
                file_names = []
                file_comments = []
                for csv_path, json_path in current_batch: 
                    file_observations.append(observeFile(csv_path))
                    file_names.append(csv_path)
                    file_comments.append(get_metadata_comment(json_path))
                send_synclist(user, file_observations)
                uuids = send_filenamelist(user, file_names)
                send_commentlist(user, uuids, file_comments)
                current_batch = []
                break
        except KeyboardInterrupt:
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_AWS_INDEX_FILE)
            break
    print('done {}/{} index : {}'.format(i+starting_point+1, len(series_ids), i+starting_point))
    save_last_good_query_index(i+starting_point, LAST_PROCESSED_AWS_INDEX_FILE)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KNPS fred-data-script command line')
    parser.add_argument("--ids", action='store_true', help="scrape series_ids and titles into local pickle file")
    parser.add_argument("--series", action="store_true", help="scrape series csvs into s3 bucket")
    parser.add_argument("--metadata", action="store_true", help="scrape series metadata into s3 bucket")
    parser.add_argument("--download",  help="download data from s3 and insert into KNPS db by supplying a username")

    args = parser.parse_args()

    if args.ids:
        get_series_ids()
    elif args.series:
        upload_series_to_s3()
    elif args.metadata:
        upload_series_metadata_to_s3()
    elif args.download:
        download_series_from_s3(args.download)
    else:
        pass
    