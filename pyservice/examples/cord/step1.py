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

from lib import get_user_id, create_data_object

USER_NAME = "AI2 CORD Bot"
USER_EMAIL = "cordbot@allenai.org"

file_ids = [
    '44efd15ada8c6e6a9de4017402163286a4b06905',
    '454a744cdd86def350e7ab253188aaef3833accd',
    'bad4f135cd64a02e182260e7c1e4d9b6f3941695',
    'b4e98770894089e276f91c1d00e58c8885708e11',
    'c28f76835909d9556c4f74299605c398ed79e25b',
    '276d1d1c20336ca2a6f54c7a95507001917e4c44',
]

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    pdf_ids = {}
    meta_ids = {}

    for file_id in file_ids:
        pdf_name = 'pdfs/' + file_id + '.pdf'

        val_comment = "Downloaded from XXXXXX on 2021-03-15"
        var_comment = "Downloaded from XXXXXX on 2021-03-15"

        pdf_obj_data = create_data_object(
            name = 'CORD PDF ' + file_id,
            ownerid = user_id,
            description = var_comment,
            pdf_file = pdf_name,
            comment = val_comment
        )

        pdf_data_obj_id = pdf_obj_data['id']
        pdf_ids[file_id] = pdf_obj_data['versions'][0]['id']

    for file_id in file_ids:
        val_comment = "Metadata from PDF {}".format(file_id)
        var_comment = "Parsed on 2021-03-15"

        json_name = 'parses/' + file_id + '.json'
        meta_obj_data = create_data_object(
            name = 'CORD Parse File ' + file_id,
            ownerid = user_id,
            description = var_comment,
            jsondata = json.load(open(json_name, 'rb')),
            comment = val_comment,
            predecessors = [pdf_ids[file_id]]
        )

        meta_data_obj_id = meta_obj_data['id']
        meta_ids[file_id] = meta_obj_data['versions'][0]['id']

    for file_id in file_ids:
        val_comment = "Segmentation data from PDF {}".format(file_id)
        var_comment = "Processed on 2021-03-16"

        json_name = 'segmentation/CORD-19-' + file_id + '.json'
        obj_data = create_data_object(
            name = 'CORD Segmentation File ' + file_id,
            ownerid = user_id,
            description = var_comment,
            jsondata = json.load(open(json_name, 'rb')),
            comment = val_comment,
            predecessors = [pdf_ids[file_id], meta_ids[file_id]]
        )
