import yaml
cfg = {}
cfg['SERVER_ADDRESS'] = 'http://lasagna.eecs.umich.edu'
cfg['SERVER_PORT'] = 8000

with open('../personal.yaml', 'r') as file:
    personal = yaml.load(file, Loader=yaml.FullLoader)
    if personal['server']:
        for k in personal['server'].keys():
            cfg[k] = personal['server'][k]

SERVER_URL = '{}:{}'.format(cfg['SERVER_ADDRESS'], cfg['SERVER_PORT'])
