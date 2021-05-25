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

from lib import get_user_id, create_data_object

USER_NAME = "Mike Anderson"
USER_EMAIL = "mrander@umich.edu"

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    # r = requests.get("https://api.covidtracking.com/v1/states/daily.json")
    data_list = json.load(open('daily.json'))
    rst = defaultdict(list)
    rst_2 = defaultdict(list)

    today = date.fromisoformat('2020-12-28') #datetime.today() - timedelta(days=185)
    twenty_days = today - timedelta(days=21)
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

    obj_data = create_data_object(
        name = 'COVID Last 20 Days',
        ownerid = user_id,
        description = var_comment,
        jsondata = dict(rst),
        comment = val_comment
    )

    data_obj_id = obj_data['id']
    version_id = obj_data['versions'][0]['id']

    # Save the data object id for use in the next step
    with open("step_1_obj_id.txt", "wt") as f:
        f.write(str(data_obj_id))
