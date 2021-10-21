## Installation
Requirements: python3, node (v10, v12 tested), npm 
Recommended: Run this in a python virtual environment.

To enable search, an ElasticSearch server is needed. The system was tested with an ES server with default settings.

To use search, set environment variables:
* ES_HOST = ElasticSearch server hostname
* ES_PORT = ElasticSearch server port (defaults to 9200 if not set)

The commandline tool sends data to the server, which is stored in a Neo4J graph database. Set the following variables with your Neo4J server, if it is not running on default localhost settings:

* NEO4J_HOST
* NEO4J_PORT (default 7687)

We also use the APOC library in Neo4j, which can be installed like so: https://neo4j.com/labs/apoc/4.2/installation/#neo4j-server

Logins are currently handled by Okta in the backend server. Ask a KNPS maintainer for client_secrets.json.

To install KNPS:
  
1. Clone this repo. Go to root directory.
2. Set up and start backend server.
  ```
cd service
pip install -r requirements.txt
alembic upgrade head
python server.py
```
3. Set up and start web frontend.
```
cd ../web
npm install
npm run dev
```
4. Set up commandline tool
```
cd ../cli
pip install -r requirements.txt
(optional) export PATH=$PATH:<ROOT_DIRECTORY>/cli/bin
```

Note: if you only want to run the commmand line tool, you can point it to our central server using `knps --server prod`. This server is likely, but not gauranteed to be running.

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
