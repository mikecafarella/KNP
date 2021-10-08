"""
Get the data from covidtracking.com.
Store it in a knpsValue.
Assign to a knpsVariable.
Everytime we run this, the knpsVariable is not changed.
But the knpsValue it points to should be updated.
i.e. a new knpsValue is created.
"""
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta, date

from lib import get_user_id, update_data_object

USER_NAME = "Mike Anderson"
USER_EMAIL = "mrander@umich.edu"

# Load the ID for the source we're using from our makeshift local store
with open("step_1_obj_id.txt", "rt") as f:
    for line in f:
        DATA_OBJECT_ID = int(line.strip())

print("Using Data Object ID: ", DATA_OBJECT_ID)

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    data_list = json.load(open('daily.json'))
    rst = defaultdict(list)
    rst_2 = defaultdict(list)

    today = date.fromisoformat('2020-12-29')
    twenty_days = today - timedelta(days=20)
    before_20_display = twenty_days.strftime('%Y-%m-%d')
    before_20 = int(twenty_days.strftime('%Y%m%d'))
    today_display = today.strftime('%Y-%m-%d')
    today = int(today.strftime('%Y%m%d'))

    for one_item in data_list:
        if one_item["date"] > today:
            continue
        if one_item["date"] < before_20:
            break
        if one_item["state"] == 'MI':
            rst[one_item["state"]].append((one_item["date"], 10*one_item["positive"]))
        else:
            rst[one_item["state"]].append((one_item["date"], one_item["positive"]))

        rst_2[one_item["date"]].append(
            (one_item["state"], one_item["positive"]))

    val_comment = "The COVID-19 cumulative positive cases for all states in the US from " + str(before_20_display) + " to " + str(today_display)
    var_comment = "The COVID-19 cumulative positive cases for all states in the US in the last 20 days"

    update_data_object(
        objectid = DATA_OBJECT_ID,
        ownerid = user_id,
        jsondata = dict(rst),
        comment = val_comment
    )
