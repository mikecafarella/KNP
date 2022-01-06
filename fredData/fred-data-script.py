
from full_fred.fred import Fred
import os
import pandas as pd
import time
# for later for performance boost 
import json
key_file = open('api_key.txt', 'r')
API_KEY = key_file.readline()
key_file.close()
os.environ['FRED_API_KEY'] = API_KEY.strip()
# ideally we just use the constructor and pass in the file name, 
# but that wasn't working so had to use this hack
fred = Fred()

# iterate thru categories and get series ids
# 0 is the root category
# can definitley clean up code here for readibility, but that is more of a secondary goal atm

# there are 8 root categories, followed by several children categories and sometimes children categories have children catogries 
# AND series associated with it, sometimes it only has one or the other, we will need to check those cases

categories = fred.get_child_categories(0)
top_level_category_ids = [(cat['id'], cat['name']) for cat in categories['categories']]
print(top_level_category_ids)
second_level_category_ids = []
for category_id, category_name in top_level_category_ids:
    children_categories = fred.get_child_categories(category_id)
    # print(children_categories)
    second_level_category_ids.extend([(cat['id'], cat['name']) for cat in children_categories['categories']])
# print(second_level_category_ids)

third_level_category_ids = []
series_ids = []
found = False
for category_id, category_name in second_level_category_ids:
    children_categories = fred.get_child_categories(category_id)
    if not children_categories['categories']:
        series_metadata = fred.get_series_in_a_category(category_id)
        if series_metadata['seriess']:
            series_ids.extend([series['id'] for series in series_metadata['seriess']])
        found  = True
        break
    else:
        third_level_category_ids.extend([(cat['id'], cat['name']) for cat in children_categories['categories']])
    if found:
        break
    # avoid hitting the max limit rate
    time.sleep(3)

