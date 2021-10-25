import os

CACHE_FILE_PROCESSING = bool(os.getenv('CASHE_FILE_PROCESSING', True))

# Create a personal.py file in this directory and set any of the above variables
# to override the default settings without setting environment variables
try:
    from personal import *
except ImportError:
    pass
