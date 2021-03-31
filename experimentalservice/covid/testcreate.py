# create_data_object(name, ownerid, description, comment, ownername='Alice', jsondata=None, image_file=None, pdf_file=None, predecessors=[]):
from lib import get_user_id, create_data_object

USER_NAME = "Jiayun Zou"
USER_EMAIL = "alicezou@umich.edu"


user_id = get_user_id(USER_EMAIL, USER_NAME)

var_comment='test search 109'
rst = {
    'answer': 109
}
val_comment = "test search 3"

obj_data = create_data_object(
    name = 'search functionality',
    ownerid = user_id,
    description = var_comment,
    jsondata = dict(rst),
    comment = val_comment,
    ownername=USER_NAME
)