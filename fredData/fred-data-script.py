
from full_fred.fred import Fred
import os
import pandas as pd
import time
# for later for performance boost 
import json
key_file = open('api_key.txt', 'r')
API_KEY = key_file.readline()
key_file.close()
SERIES_JSON_FILE = "series_ids.json"
os.environ['FRED_API_KEY'] = API_KEY.strip()
# ideally we just use the constructor and pass in the file name, 
# but that wasn't working so had to use this hack
fred = Fred()
# 0 is the root category
if not os.path.isfile(SERIES_JSON_FILE):
    # this exists to get all the ids of the series we want to scrape ultimately 
    categories = fred.get_child_categories(0)
    top_level_category_ids = [(cat['id'], cat['name']) for cat in categories['categories']]
    category_queue = top_level_category_ids[:]
    series_ids = set()
    #this is kind of close to the API rate limit, which appears to around 40ish calls/minute 
    batch_size = 21
    count = 0
    while category_queue:
        new_category_queue = []
        for category_id, category_name in category_queue:
            children_categories = fred.get_child_categories(category_id)
            series_metadata = fred.get_series_in_a_category(category_id)
            if (children_categories['categories']):
                new_category_queue.extend([(cat['id'], cat['name']) for cat in children_categories['categories']])
            if (series_metadata['seriess']):
                for series in series_metadata['seriess']:
                    series_ids.add(series['id'])
            count += 1
            if (count % batch_size) == 0:
                print("taking a nap!")
                time.sleep(60)
        category_queue = new_category_queue

    print(len(series_ids))
    with open(SERIES_JSON_FILE, 'w') as f:
        json.dump(list(series_ids), f)
    print("done")
else:
    with open(SERIES_JSON_FILE, 'r') as f:
        series_ids = json.load(f)
    


