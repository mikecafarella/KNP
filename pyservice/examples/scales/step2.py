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
from urllib.request import urlopen

from lib import get_user_id, create_data_object, update_data_object

USER_NAME = "Mike Anderson"
USER_EMAIL = "mrander@umich.edu"

sample_data_file = "data/Unemployment_data_2019.csv"
sample_data_file2 = "data/all_court_records.csv"
sample_data_file3 = "data/judicial_districts.csv"
sample_data_file4 = "data/fips_counties.csv"

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)
    user_id2 = get_user_id("andrewpaley2022@u.northwestern.edu", "Andrew Paley")
    user_id3 = get_user_id("alicezou@umich.edu", "Jiayun Zou")
    user_id4 = get_user_id("michjc@csail.mit.edu", "Michael Cafarella")
    user_id5 = get_user_id("ctm310@yahoo.com", "Carol McLaughlin")

    map_func = """def tei_to_json(dobj_id):
    from doc2json.grobid2json.tei_to_json import convert_tei_xml_soup_to_s2orc_json
    from bs4 import BeautifulSoup
    from io import StringIO

    input_data = get_dobj_contents(dobj_id)
    xml_file = StringIO(input_data.decode())

    paper_id = dobj_id
    pdf_hash = ''
    soup = BeautifulSoup(xml_file, "xml")
    paper = convert_tei_xml_soup_to_s2orc_json(soup, paper_id, pdf_hash)

    return {'contents': json.dumps(paper.as_json(), indent=2).encode(), 'datatype': '/datatypes/json', 'mimetype': 'application/json', 'predecessors': []}"""

    code_obj_data = update_data_object(
        objectid = 48,
        ownerid = user_id,
        code = map_func,
        comment = 'CORD 19 JSON format'
    )
