# this file creates the data needed for the classifier
import pandas as pd
import json 
import numpy as np
import os
import boto3
import pickle
import botocore

DATA_DIR = 'data'
LAST_PROCESSED_INDEX_FILE = 'last_processed_index.json'
DATASET_NPZ_FILE = 'data_set.npz'

# aws_credentials = open("aws_keys.json", 'r')
# aws_keys = json.load(aws_credentials)
# ACCESS_KEY_ID = aws_keys['access_key_id']
# SECRET_ACCESS_KEY = aws_keys['secret_access_key']
# aws_credentials.close()
# os.environ["AWS_DEFAULT_REGION"] = 'us-east-1'
# os.environ["AWS_ACCESS_KEY_ID"] = ACCESS_KEY_ID
# os.environ["AWS_SECRET_ACCESS_KEY"] = SECRET_ACCESS_KEY
# BUCKET_NAME = 'knps-data'
# s3 = boto3.resource('s3')
# SERIES_FOLDER = 'FRED'
# SERIES_PICKLE_FILE = "series_ids.pickle"


def save_last_index(index, file_name):
    with open(file_name, 'w') as lpi:
        json.dump({"index": index}, lpi)

def get_starting_point(index_file):
    starting_point = 0
    if os.path.isfile(index_file):
        with open(index_file, 'r') as lpi:
            starting_point = json.load(lpi)['index']
    return starting_point

# this will certainly change 
FILE_TYPE_NUMERICAL_MAP = {
    'text/csv': 0,
    'image/png': 1,
    'application/pdf': 2,
}
def get_num_cols(csv_path):
    df = pd.read_csv(csv_path)
    cols = [col for col in df.columns if "Unnamed" not in col]
    return len(cols)

def change_title(num_cols):
    output = np.array([FILE_TYPE_NUMERICAL_MAP['text/csv'], num_cols])
    input = np.array([FILE_TYPE_NUMERICAL_MAP['text/csv'], num_cols])
    vector = np.concatenate((input, output), axis=0)
    return np.array([vector])


def drop_column(num_cols):
    output = np.array([FILE_TYPE_NUMERICAL_MAP['text/csv'], num_cols-1])
    input = np.array([FILE_TYPE_NUMERICAL_MAP['text/csv'], num_cols])
    vector = np.concatenate((input, output), axis=0)
    return np.array([vector])

def make_viz(num_cols):
    output = np.array([FILE_TYPE_NUMERICAL_MAP['image/png'], 0])
    input = np.array([FILE_TYPE_NUMERICAL_MAP['text/csv'], num_cols])
    vector = np.concatenate((input, output), axis=0)
    return np.array([vector])

OPERATION_LABEL_MAP = {
    make_viz: 0,
    change_title: 1,
    drop_column: 2,
}

LABEL_OPERATION_MAP = {v:k.__name__ for k, v in OPERATION_LABEL_MAP.items()}

def get_data_set():
    X = np.empty((0,4), int)
    y = np.array([])
    if os.path.isfile(DATASET_NPZ_FILE):
       with open(DATASET_NPZ_FILE, 'rb') as f:
           data = np.load(f)
           X = data['X']
           y = data['y']
    return X, y

# TODO: will be useful once more progress is made on the classifier
# def generate_data_set():
#     ending_point = 1500
#     successes = 0
#     s3_series_folder = 'FRED'
#     starting_point = get_starting_point(LAST_PROCESSED_INDEX_FILE)
#     X, y = get_data_set()
#     with open(SERIES_PICKLE_FILE, 'rb') as f:
#         series_ids = pickle.load(f)
#     bucket = s3.Bucket(BUCKET_NAME)
#     for i, (_, series_title) in enumerate(series_ids[starting_point:]):
#         print(successes, series_title)
#         try:
#             if (successes+starting_point) == ending_point:
#                 print("caught up")
#                 break
#             file_path = "{}/{}.csv".format(DATA_DIR, series_title)
#             bucket.download_file("{}/{}.csv".format(s3_series_folder, series_title), file_path)
#             num_cols = get_num_cols(file_path)
#             for func, label in OPERATION_LABEL_MAP.items():
#                 X = np.append(X, func(num_cols), axis=0) 
#                 y = np.append(y, [label], axis=0)
            
#         except botocore.exceptions.ClientError:
#             continue
#         except FileNotFoundError:
#             continue
#         successes += 1
#     save_last_index(i+starting_point, LAST_PROCESSED_INDEX_FILE)
#     with open(DATASET_NPZ_FILE, 'wb') as f:
#         np.savez(f, X=X, y=y)

if __name__ == "__main__":
    # if not os.path.isdir(DATA_DIR):
    #     os.system("mkdir {}".format(DATA_DIR))
    # # drop_column('Book1.csv')
    # generate_data_set()
    # # get_data_set()
    pass
