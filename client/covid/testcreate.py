# create_data_object(name, ownerid, description, comment, ownername='Alice', jsondata=None, image_file=None, pdf_file=None, predecessors=[]):
from lib import get_user_id, create_data_object

USER_NAME = "Jiayun Zou"
USER_EMAIL = "alicezou@umich.edu"


user_id = get_user_id(USER_EMAIL, USER_NAME)

var_comment='Honors Convocation is tonight'
rst = {
    'Honors Convocation': 2021 
}
val_comment = "Honors Convocation is tonight"

obj_data = create_data_object(
    name = 'Honors Convocation',
    ownerid = user_id,
    description = var_comment,
    jsondata = dict(rst),
    comment = val_comment,
    ownername=USER_NAME
)