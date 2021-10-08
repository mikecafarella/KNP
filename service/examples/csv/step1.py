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

from lib import get_user_id, create_data_object, update_data_object

USER_NAME = "Jack Gelinas"
USER_EMAIL = "gelinas.j@northeastern.edu"

sample_data_file = "data/sample-data.csv"

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    csv_obj_data = create_data_object(
        name = 'Sample extracted data',
        ownerid = user_id,
        description = 'Sample CSV data file',
        datafile = sample_data_file,
        comment = 'Predicate, subject, object'
    )

    data_obj_id = csv_obj_data['id']

    # This is an example of how to update the contents of a data
    # object. Since we just have a single sample file, though, it
    # re-uploads that data.
    csv_obj_data = update_data_object(
        objectid = data_obj_id,
        ownerid = user_id,
        datafile = sample_data_file,
        comment = 'Updated: Predicate, subject, object'
    )
