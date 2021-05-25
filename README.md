## Installation
Requirements: python3, node (v12 tested), npm 
Recommended: Run this in a python virtual environment.

1. Clone this repo. Go to root directory.
2. Set up and start backend server.
  ```
cd pyservice
pip install -r requirments.txt
alembic upgrade head
python server.py
```
3. Set up and start frontend.
```
cd ../experimentalservice
npm install
npm run dev
```

To install demo data, go to pyservice directory and run `bootstrap_demo.sh`


To reset the database, remove the current database and reinitialize; also clear out elasticsearch index. 
From the pyservice directory:
```
rm knps.db
alembic upgrade head
python delete_es_index.py
```

## Older: 

See our documentation for installation instructions and examples:

https://mikecafarella.github.io/KNP/
