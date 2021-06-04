"""
Apply funtions to PDFs
"""
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta

from lib import get_user_id, apply_function

USER_NAME = "Rodney K"
USER_EMAIL = "rodneyk@allenai.org"

file_ids = {
    '44efd15ada8c6e6a9de4017402163286a4b06905': 4,
    '454a744cdd86def350e7ab253188aaef3833accd': 5,
    'bad4f135cd64a02e182260e7c1e4d9b6f3941695': 6,
    'b4e98770894089e276f91c1d00e58c8885708e11': 7,
    'c28f76835909d9556c4f74299605c398ed79e25b': 8,
    '276d1d1c20336ca2a6f54c7a95507001917e4c44': 9,
}

full_text_xml = 22
structure_extractor = 23


if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    for file_id, dobjid in file_ids.items():
        pdf_obj_data = apply_function(
            function_id = structure_extractor,
            dataobject_id = dobjid,
            name = 'Extracted Structure for PDF {}'.format(file_id),
            ownerid = user_id,
            datatype = '/datatypes/json',
            description = 'JSON-formatted PDF structure extraction',
            comment = 'PDF: {}'.format(file_id)
        )

        pdf_obj_data = apply_function(
            function_id = full_text_xml,
            dataobject_id = dobjid,
            name = 'XML Full Text for PDF {}'.format(file_id),
            ownerid = user_id,
            datatype = '/datatypes/xml',
            description = 'XML-formatted full text parse',
            comment = 'PDF: {}'.format(file_id)
        )
