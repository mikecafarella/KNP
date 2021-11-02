import os

KNPS_SERVER_DEV = os.getenv('KNPS_SERVER_DEV', '127.0.0.1:5000')
KNPS_SERVER_PROD = os.getenv('KNPS_SERVER_PROD', 'ec2-3-224-14-41.compute-1.amazonaws.com:5000')

CACHE_FILE_PROCESSING = bool(os.getenv('CASHE_FILE_PROCESSING', True))

# Create a personal.py file in this directory and set any of the above variables
# to override the default settings without setting environment variables
try:
    from personal import *
except ImportError:
    pass
