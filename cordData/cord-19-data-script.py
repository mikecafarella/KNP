# import json
# import os
# from datetime import datetime
# from datetime import timedelta
# import tarfile
# from functools import reduce, partial
# from typing import Any, Callable, Dict, List, Sequence, TypeVar, Union, overload
# from urllib.request import urlopen
import requests
import shutil
from bs4 import BeautifulSoup
import lxml

#TODO: s3 bucket credentials
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

#Extract CORD-10 release dates
source = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html').text
soup = BeautifulSoup(source, 'lxml')
table = soup.find('table')
entries = table.find_all('tr')[1:]
dates = map(lambda entry : entry.td.text, entries)
print(list(dates))

#Iterate over all dates and do this: 

#Get url for CORD-19 Paper metadata
s3bucket_url = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/"
metadata_url = s3bucket_url + date + "/metadata.csv"

#Download the metadata.csv file
res = requests.get(metadata_url, stream=True)
if res.status_code != 200:
  print(f"Failed to download {url}: Got status {res.status_code}")
  exit()
else:
  print(f"Processing {url} ... ", end="")
  res.raw.decode_content = True
  with open("metadata.csv", 'wb') as f:
    shutil.copyfileobj(res.raw, f)
  print("Download complete.")

#Upload to s3


#Download from s3
