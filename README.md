## Installation
Requirements: python3, node (v10, v12 tested), npm 
Recommended: Run this in a python virtual environment.

To enable search, an ElasticSearch server is needed. The system was tested with an ES server with default settings.

To use search, set environment variables:
* ES_HOST = ElasticSearch server hostname
* ES_PORT = ElasticSearch server port (defaults to 9200 if not set)

To install KNPS:
  
1. Clone this repo. Go to root directory.
2. Set up and start backend server.
  ```
cd service
pip install -r requirements.txt
alembic upgrade head
python server.py
```
3. Set up and start frontend.
```
cd ../client
npm install
npm run dev
```

The initial database contains data that would be loaded with the following instructions, so don't run them, unless you want to reset.

---

To install demo data, go to service directory and run `bootstrap_demo.sh`


To reset the database, remove the current database and reinitialize; also clear out elasticsearch index. 
From the pyservice directory:
```
rm knps.db
alembic upgrade head
python delete_es_index.py
```

## Older, now defunct: 

See our documentation for installation instructions and examples:

https://mikecafarella.github.io/KNP/
