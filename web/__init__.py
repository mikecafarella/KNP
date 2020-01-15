from flask import Flask, g
import os

app = Flask(__name__)

import web.views
import web.db_utils

# web.db_utils.drop_db()
web.db_utils.init_db()

### Remove all tmp files
filelist = os.listdir("web/static/tmp")
for f in filelist:
    os.remove(os.path.join("web/static/tmp", f))


# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response
