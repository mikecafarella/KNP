import json
import os
import boto3
import sys
import time
import requests
import shutil
from bs4 import BeautifulSoup
import lxml

#s3 bucket credentials
aws_credentials = open("aws_config.json", 'r')
aws_keys = json.load(aws_credentials)
ACCESS_KEY_ID = aws_keys['access_key_id']
SECRET_ACCESS_KEY = aws_keys['secret_access_key']
REGION = aws_keys['region']
aws_credentials.close()

BUCKET_NAME = 'knps-data'
os.environ["AWS_DEFAULT_REGION"] = REGION
os.environ["AWS_ACCESS_KEY_ID"] = ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = SECRET_ACCESS_KEY
s3 = boto3.resource('s3')

#Extract CORD-10 release dates
source = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html').text
soup = BeautifulSoup(source, 'lxml')
table = soup.find('table')
entries = table.find_all('tr')[1:]
dates = list(map(lambda entry : entry.td.text, entries))

#Uploading metadata.csv's to s3
for date in dates[-3:-1]:
  #Get url for CORD-19 Paper metadata
  s3bucket_url = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/"
  metadata_url = s3bucket_url + date + "/metadata.csv"
  new_file_url = None

  #Download the metadata.csv file and upload to s3
  res = requests.get(metadata_url, stream=True)
  if res.status_code != 200:
    print(f"Failed to download {metadata_url}: Got status {res.status_code}")
    exit()
  else:
    #Download metadata.csv
    print(f"Processing {metadata_url} ... ", end="")
    res.raw.decode_content = True
    new_file_url = "metadata_" + date + ".csv"
    with open(new_file_url, 'wb') as f:
      shutil.copyfileobj(res.raw, f)
    print("Download complete.")

    #Upload to s3
    print(f"Uploading {metadata_url} to s3 ... ", end="")
    object_key = "CORD19/" + new_file_url
    s3.meta.client.upload_file(Filename = new_file_url, Bucket= BUCKET_NAME, Key = object_key)
    print("Upload complete.")


#Download from s3


#Sync with KNPS
