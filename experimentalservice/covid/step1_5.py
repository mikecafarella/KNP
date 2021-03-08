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
from datetime import datetime, timedelta

from lib import get_user_id

USER_NAME = "Mike Anderson"
USER_EMAIL = "mrander@umich.edu"

DATA_OBJECT_ID = 20

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    r = requests.get("https://api.covidtracking.com/v1/states/daily.json")
    data_list = r.json()
    rst = defaultdict(list)
    rst_2 = defaultdict(list)

    today = datetime.today() - timedelta(days=1)
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
        rst[one_item["state"]].append((one_item["date"], one_item["positive"]))
        rst_2[one_item["date"]].append(
            (one_item["state"], one_item["positive"]))

    val_comment = "The COVID-19 cumulative positive cases for all states in the US from " + str(before_20_display) + " to " + str(today_display)
    var_comment = "The COVID-19 cumulative positive cases for all states in the US in the last 20 days"



    url = "http://localhost:3000/api/updatedataobj"
    jsondata = dict(rst)
    data = {
        'metadata': {
            'ownerid': user_id,
            'dobjid': DATA_OBJECT_ID,
            'comment': val_comment,
            'datatype': '/datatypes/json',
            'jsondata': jsondata
        }
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
