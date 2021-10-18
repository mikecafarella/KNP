import yaml
import os

this_dir = os.path.dirname(os.path.realpath(__file__))

cfg = {}
cfg['SERVER_ADDRESS'] = 'http://lasagna.eecs.umich.edu'
cfg['SERVER_PORT'] = 8000
cfg['SERVER_ENVIRONMENT'] = 'production'

try:
    with open(this_dir + '/../personal.yaml', 'r') as file:
        personal = yaml.load(file, Loader=yaml.FullLoader)
        if personal['server']:
            for k in personal['server'].keys():
                cfg[k] = personal['server'][k]
except:
    print("persona.yaml failed to load for server.py")
    pass

# These are the variables that can be exported
SERVER_ENVIRONMENT = cfg['SERVER_ENVIRONMENT']
SERVER_URL = '{}:{}'.format(cfg['SERVER_ADDRESS'], cfg['SERVER_PORT'])
