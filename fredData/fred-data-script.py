
from full_fred.fred import Fred
import os
import pandas as pd
import time
import pickle
import json
import boto3
import sys
sys.path.append("../cli/src/knps")
from io import StringIO
import argparse


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
# s3_client = boto3.client('s3')

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

def download_series_from_s3(username):
    os.system("python3 ../cli/src/knps/knps.py --login_temp {}".format(username))
    os.system("python3 ../cli/src/knps/knps.py --store True")
    with open(LAST_PROCESSED_INDEX_FILE, 'r') as epi:
        ending_point = json.load(epi)['index']

    if not os.path.isdir(OUTPUT_FOLDER):
        os.system("mkdir {dir}".format(dir=OUTPUT_FOLDER))
        os.system("python3 ../cli/src/knps/knps.py --watch {dir}".format(dir=OUTPUT_FOLDER))

    s3_series_folder = 'FRED'
    s3_metadata_folder = 'FRED-METADATA'
    bucket = s3.Bucket(BUCKET_NAME)
    starting_point = get_starting_point(LAST_PROCESSED_AWS_INDEX_FILE)
    batch_size = 100
    with open(SERIES_PICKLE_FILE, 'rb') as f:
        series_ids = pickle.load(f)
    print("{}/{} index start {}".format(starting_point+1, len(series_ids), starting_point))
    for i, (_, series_title) in enumerate(series_ids[starting_point:]):
        print(series_title)
        try:
            bucket.download_file("{}/{}.csv".format(s3_series_folder, series_title), "{}/{}.csv".format(OUTPUT_FOLDER, series_title))
            bucket.download_file("{}/{}.json".format(s3_metadata_folder, series_title), "{}/{}.json".format(OUTPUT_FOLDER, series_title))
            if (i+1) % batch_size == 0:
                os.system("python3 ../cli/src/knps/knps.py --sync")
            if (i+starting_point) == ending_point:
                print("caught up")
                break
        except Exception as e:
            print(repr(e))
            save_last_good_query_index(i+starting_point, LAST_PROCESSED_AWS_INDEX_FILE)
            break
    print('done {}/{} index : {}'.format(i+starting_point+1, len(series_ids), i+starting_point))

if __name__ == "__main__":
    testing = True
    
    parser = argparse.ArgumentParser(description='KNPS fred-data-script command line')
    parser.add_argument("--ids", action='store_true', help="scrape series_ids and titles into local pickle file")
    parser.add_argument("--series", action="store_true", help="scrape series csvs into s3 bucket")
    parser.add_argument("--metadata", help="scrape series metadata into s3 bucket")
    parser.add_argument("--download",  help="download data from s3 and insert into KNPS db by supplying a username")
    
    args = parser.parse_args()

    if args.ids:
        get_series_ids()
    elif args.series:
        upload_series_to_s3()
    elif args.metadata:
        upload_series_metadata_to_s3()
    else:
        os.system("rm ~/.knpsdb") ##NEED TO DO THIS SO IT DOES NOT THINK THINGS R INACCURATELY PROCCESSED
        # print(args.download)
        download_series_from_s3(args.download, OUTPUT_FOLDER)
    