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

USER_NAME = "Rodney K"
USER_EMAIL = "rodneyk@allenai.org"

function1 = """def full_text_process(dobj_id):
   import requests
   url = 'http://s2-grobid-tokens.us-west-2.elasticbeanstalk.com/api/processFulltextDocument'
   input_data = get_dobj_contents(dobj_id)
   files = {'input': input_data}
   r = requests.post(url, files=files)
   return r.text"""

function2 = """def pdf_structure(dobj_id):
   import requests
   url = 'http://s2-grobid-tokens.us-west-2.elasticbeanstalk.com/api/processPdfStructure'
   input_data = get_dobj_contents(dobj_id)
   files = {'input': input_data}
   r = requests.post(url, files=files)
   return r.json()"""

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)

    pdf_obj_data = create_data_object(
        name = 'AI2 Full Text PDF Processor',
        ownerid = user_id,
        description = 'Processes PDF to extract text and structure in XML format',
        code = function1,
        comment = 'XML formatted PDF text'
    )

    pdf_obj_data = create_data_object(
        name = 'AI2 PDF Structure Extractor',
        ownerid = user_id,
        description = 'Extracts structure of PDF text; outputs as JSON',
        code = function2,
        comment = 'JSON formatted PDF structure'
    )
