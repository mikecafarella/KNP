
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

OUTPUT_FOLDER = 'output'
LAST_PROCESSED_INDEX_FILE = 'last_processed_index.json'

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

def upload_series_to_s3():
    # upload csvs to aws s3 bucket
    starting_point = 110
    if os.path.isfile(LAST_PROCESSED_INDEX_FILE):
        with open(LAST_PROCESSED_INDEX_FILE, 'r') as lpi:
            starting_point = json.load(lpi)['index']

    # respect API rate limits
    batch_size = 120
    with open(SERIES_PICKLE_FILE, 'rb') as f:
        series_ids = pickle.load(f)
    print("{}/{} index start {}".format(starting_point+1, len(series_ids), starting_point))
    for i, (series_id, series_title) in enumerate(series_ids[starting_point:]):
        try:
            series_df = fred.get_series_df(series_id)
            csv_name = "{title}.csv".format(title=series_title)
            csv_buffer = StringIO()
            series_df.to_csv(csv_buffer)
            s3.Object(BUCKET_NAME, csv_name).put(Body=csv_buffer.getvalue())
            if (i+1)%batch_size == 0:
                print('nap time!')
                time.sleep(60)
        # if I want to stop, this will let me know where the program needs to pick up again
        except KeyboardInterrupt:
            save_last_good_query_index(i+starting_point)
            break
        # handle any other exception, namely API limit reached 
        except:
            save_last_good_query_index(i+starting_point)
            break
    print('done {}/{} index : {}'.format(i+starting_point+1, len(series_ids), i+starting_point))

def save_last_good_query_index(index):
    with open(LAST_PROCESSED_INDEX_FILE, 'w') as lpi:
        json.dump({"index": index}, lpi)

def download_series_from_s3(series_titles, logged_in=False):
    if not logged_in:
        os.system("python3 ../cli/src/knps/knps.py --login_temp Steve")

    if not os.path.isdir(OUTPUT_FOLDER):
        os.system("mkdir {dir}".format(dir=OUTPUT_FOLDER))
        os.system("python3 ../cli/src/knps/knps.py --watch {dir}".format(dir=OUTPUT_FOLDER))

    for series_title in series_titles:
        s3.Bucket(BUCKET_NAME).download_file(series_title, "{dir}/{csv}".format(dir=OUTPUT_FOLDER, csv=series_title))
        os.system('python3 ../cli/src/knps/knps.py --sync') 

if __name__ == "__main__":
    testing = True
    # os.system("rm ~/.knpsdb") ##NEED TO DO THIS SO IT DOES NOT THINK THINGS R INACCURATELY PROCCESSED
    if not os.path.isfile(SERIES_PICKLE_FILE):
        get_series_ids()
    else:
        # count = 0
        # for i in s3.Bucket(BUCKET_NAME).objects.all():
        #     count += 1
        # print(count)
        upload_series_to_s3()
        # if testing:
        #     os.system("rm -r {}".format(OUTPUT_FOLDER))
        # test = "Income Inequality in Tunica County, MS.csv"
        # download_series_from_s3([test])
        # insert_data_into_knps()
