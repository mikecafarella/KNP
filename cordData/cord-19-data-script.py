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

#Extract latest CORD-19 release date
source = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html').text
soup = BeautifulSoup(source, 'lxml')
table = soup.find('table')
latest_entry = table.find_all('tr')[1]
date = latest_entry.td.text

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
