from flask import Flask, abort, request, jsonify
from flask_cors import CORS

from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from sqlalchemy import select

from models import *
from functions import execute_function, get_dobj_contents
from database import SessionLocal, engine

import base64
import json
import datetime
import asyncio

from elasticsearch import Elasticsearch
import uuid
# This is just a temporary thing for demos so we can all run off diferent indexes on the elsasticsearch server
machine_id = uuid.UUID(int=uuid.getnode())

ES_INDEX = 'knps-00000000-0000-0000-0000-acde48001122' #'knps-{}'.format(machine_id)
ES_HOST = FOO = os.getenv('ES_HOST')

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knps.db'
db = SessionLocal()
ma = Marshmallow(app)
api = Api(app)

loop = asyncio.get_event_loop()

# Decorator to allow a function to run in the background, fire-and-forget style
def background(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if callable(f):
            return loop.run_in_executor(None, f, *args, **kwargs)
        else:
            raise TypeError('Task must be a callable')
    return wrapped

@background
def es_store_record(index_name, doc_id, record):
    if ES_HOST:
        _es = None
        _es = Elasticsearch([{'host': ES_HOST, 'port': 9200}])
        try:
            print("START SEARCH SUBMISSION:", record)
            outcome = _es.index(index=index_name, id=doc_id, body=record)
            print("ELASTICSEARCH:", outcome)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))
    else:
        print("WARNING: ES_HOST environment variable not defined. Data not saved to ElasticSearch.")

def es_delete_index():
    if ES_HOST:
        _es = None
        _es = Elasticsearch([{'host': ES_HOST, 'port': 9200}])
        _es.indices.delete(index=ES_INDEX, ignore=[400, 404])
    else:
        print("WARNING: ES_HOST environment variable not defined. Search index not deleted.")

class BlobField(ma.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return base64.b64encode(value).decode('ascii')

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return base64.b64decode(value)
        except ValueError as error:
            raise ma.ValidationError("Error decoding blob") from error


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email")
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class DataContentsSchema(ma.Schema):
    class Meta:
        model = DataContents
        fields = ('id',
                  'mimetype',
                  'contents')
    contents = BlobField()

contents_schema = DataContentsSchema()

class DataVersionLightSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'comment',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested(UserSchema)
    contents = ma.Nested(DataContentsSchema)
    predecessors = ma.Nested('DataVersionLightSchema', many=True)
    generators = ma.Nested('DataVersionLightSchema', many=True)

class DataVersionFullSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'dataobject',
                  'comment',
                  'contents',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested('UserSchema')
    contents = ma.Nested('DataContentsSchema')
    dataobject = ma.Nested('DataObjectSchema', exclude=['versions'])
    predecessors = ma.Nested('DataVersionFullSchema', many=True)
    generators = ma.Nested('DataVersionFullSchema', many=True)


version_full_schema = DataVersionFullSchema()

class DataVersionSchema(ma.Schema):
    class Meta:
        model = DataVersion
        fields = ('id',
                  'owner',
                  'datatype',
                  'comment',
                  'contents',
                  'predecessors',
                  'generators',
                  'created')

    owner = ma.Nested(UserSchema)
    contents = ma.Nested(DataContentsSchema)
    predecessors = ma.Nested('DataVersionLightSchema', many=True)
    generators = ma.Nested('DataVersionLightSchema', many=True)

version_schema = DataVersionSchema()

class DataObjectSchema(ma.Schema):
    class Meta:
        model = DataObject
        fields = ('id',
                  'name',
                  'description',
                  'owner',
                  'created',
                  'versions')

    owner = ma.Nested(UserSchema)
    versions = ma.Nested(DataVersionSchema, many=True, exclude=['contents'])


dobj_schema = DataObjectSchema()
dobjs_schema = DataObjectSchema(many=True)


class UserListResource(Resource):
    def get(self):
        users = db.query(User)
        return users_schema.dump(users)

    def post(self):
        # todo: validation & integrate signup stuff
        user = db.query(User).filter_by(email = request.json['email']).first()

        if not user:
            user = User(
                name = request.json['name'],
                email = request.json['email']
            )
            db.add(user)
            db.commit()
        return user_schema.dump(user)

api.add_resource(UserListResource, '/users')

class UserResource(Resource):
    def get(self, user_id):
        user = db.query(User).filter_by(id = user_id).first()

        if not user:
            abort(404)

        return user_schema.dump(user)

api.add_resource(UserResource, '/users/<int:user_id>')

class DataObjectsResource(Resource):
    def get(self):
        dobj = db.query(DataObject)

        return dobjs_schema.dump(dobj)


    def post(self):
        # todo: validation & integrate signup stuff
        metadata = json.load(request.files['metadata'])

        new_dobj = DataObject(
            owner_id = metadata['owner_id'],
            name = metadata['name'],
            description = metadata['description']
        )
        db.add(new_dobj)

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = metadata['datatype'],
            dataobject = new_dobj,
            predecessors = [db.query(DataVersion).get(x) for x in metadata['predecessors']]
        )
        db.add(new_version)

        if metadata.get('data', None):
            contents = json.dumps(metadata['data']).encode()
        elif request.files.get('datafile', None):
            contents = request.files['datafile'].read()
        else:
            # todo: get rid of jsondata/imgdata/etc.
            if new_version.datatype == '/datatypes/json':
                contents = json.dumps(metadata['jsondata']).encode()
            elif new_version.datatype == '/datatypes/img':
                contents = request.files['imgpath'].read()
            elif new_version.datatype == '/datatypes/pdf':
                contents = request.files['pdfpath'].read()
            elif new_version.datatype == '/datatypes/function':
                contents = json.dumps(metadata['code']).encode()
            else:
                contents = None


        new_contents = DataContents(
            mimetype = metadata['mimetype'],
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(new_dobj.id),
            'owner': new_dobj.owner.name,
            'name': new_dobj.name,
            'description': new_dobj.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }

        doc_id = 'X{}'.format(new_dobj.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(dobj_schema.dump(new_dobj))

api.add_resource(DataObjectsResource, '/dobjs')

class DataObjectResource(Resource):
    def get(self, dobj_id):
        dobj_id = int(dobj_id.replace('X', ''))
        dobj = db.query(DataObject).filter_by(id = dobj_id).first()
        if not dobj:
            abort(404)

        return jsonify(dobj_schema.dump(dobj))


api.add_resource(DataObjectResource, '/dobjs/<string:dobj_id>')

class DataVersionsResource(Resource):
    def post(self):
        # todo: validation & integrate signup stuff
        metadata = json.load(request.files['metadata'])
        dataobject = db.query(DataObject).get(metadata['dobj_id'])

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = metadata['datatype'],
            dataobject = dataobject,
            predecessors = [db.query(DataVersion).get(x) for x in metadata['predecessors']]
        )
        db.add(new_version)

        # todo: get rid of jsondata/imgdata/etc.
        if metadata.get('data', None):
            contents = json.dumps(metadata['data']).encode()
        elif request.files.get('datafile', None):
            contents = request.files['datafile'].read()
        else:
            # todo: get rid of jsondata/imgdata/etc.
            if new_version.datatype == '/datatypes/json':
                contents = json.dumps(metadata['jsondata']).encode()
            elif new_version.datatype == '/datatypes/img':
                contents = request.files['imgpath'].read()
            elif new_version.datatype == '/datatypes/pdf':
                contents = request.files['pdfpath'].read()
            elif new_version.datatype == '/datatypes/function':
                contents = json.dumps(metadata['code']).encode()
            else:
                contents = None

        new_contents = DataContents(
            mimetype = metadata['mimetype'],
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(dataobject.id),
            'owner': dataobject.owner.name,
            'name': dataobject.name,
            'description': dataobject.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }
        doc_id = 'X{}'.format(dataobject.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(version_full_schema.dump(new_version))

api.add_resource(DataVersionsResource, '/versions')

class DataVersionResource(Resource):
    def get(self, v_id):
        v = db.query(DataVersion).filter_by(id = v_id).first()
        print(v.contents.id)
        if not v:
            abort(404)

        return jsonify(version_full_schema.dump(v))

api.add_resource(DataVersionResource, '/version/<int:v_id>')

class DataContentsResource(Resource):
    def get(self, v_id):
        v = db.query(DataContents).filter_by(id = v_id).first()
        if not v:
            abort(404)

        return contents_schema.dump(v)

    def post(self):
        # todo: validation & integrate signup stuff
        # new_dobj = DataObject(
        #     owner_id = request.json['owner_id'],
        #     name = request.json['name'],
        #     description = request.json['description']
        # )
        # db.add(new_dobj)
        # db.commit()
        return dobj_schema.dump(new_dobj)

# api.add_resource(DataVersionResource, '/version')
api.add_resource(DataContentsResource, '/contents/<int:v_id>')

class FunctionsResource(Resource):
    def get(self):
        dobj = db.query(DataObject).filter(DataObject.versions.any(datatype = '/datatypes/function'))

        return dobjs_schema.dump(dobj)

api.add_resource(FunctionsResource, '/functions')


class FunctionResource(Resource):
    def get(self, f_id, dobj_id):
        # params = ['fips_txt', 'Median_Household_Income_2019']
        params = request.args.get('params', '').strip()

        if params:
            params = [x.strip() for x in params.split(',')]

        output = execute_function(f_id, [dobj_id], params)

        output['contents'] = base64.b64encode(output['contents']).decode('ascii')

        return output

    def post(self, f_id, dobj_id):
        metadata = json.load(request.files['metadata'])

        params = metadata.get('params', '').strip()

        if params:
            params = [x.strip() for x in params.split(',')]

        output = execute_function(f_id, [dobj_id], params)

        func = db.query(DataObject).get(f_id)

        # TODO: abstract the data object creation out, since we have it in here multiple times
        new_dobj = DataObject(
            owner_id = metadata['owner_id'],
            name = metadata['name'],
            description = metadata['description']
        )
        db.add(new_dobj)

        datatype = metadata['datatype']
        mimetype = metadata['mimetype']

        pred_obj = db.query(DataObject).get(dobj_id)
        predecessors = [pred_obj.versions[0]]

        if type(output) != str:
            if output.get('datatype', None):
                datatype = output.get('datatype', None)
            if output.get('mimetype', None):
                mimetype = output.get('mimetype', None)
            if output.get('predecessors', None):
                p_ids = output.get('predecessors', [])
                for p in p_ids:
                    pred_obj = db.query(DataObject).get(p)
                    predecessors.append(pred_obj.versions[0])

        print(predecessors)

        new_version = DataVersion(
            owner_id = metadata['owner_id'],
            comment = metadata['comment'],
            datatype = datatype,
            dataobject = new_dobj,
            predecessors = predecessors,
            generators = [func.versions[0]]
        )
        db.add(new_version)

        # TODO: Clean this up
        if new_version.datatype == '/datatypes/json':
            contents = json.dumps(output).encode()
        elif new_version.datatype == '/datatypes/img':
            contents = output['contents']
        elif new_version.datatype == '/datatypes/pdf':
            contents = output['contents']
        elif new_version.datatype == '/datatypes/function':
            contents = output.encode()
        elif new_version.datatype == '/datatypes/xml':
            contents = output.encode()
        else:
            contents = output['contents']


        new_contents = DataContents(
            mimetype = mimetype,
            contents = contents,
            dataversion = new_version
        )
        db.add(new_contents)

        db.commit()

        # Send it to Elasticsearch
        record =  {
            'url': 'http://localhost:3000/dobj/X{}'.format(new_dobj.id),
            'owner': new_dobj.owner.name,
            'name': new_dobj.name,
            'description': new_dobj.description,
            'comment': new_version.comment,
            'pytype': new_version.datatype,
            'timestamp': new_version.created.isoformat()
        }

        doc_id = 'X{}'.format(new_dobj.id)
        es_store_record(ES_INDEX, doc_id, record)

        return jsonify(dobj_schema.dump(new_dobj))


api.add_resource(FunctionResource, '/function/<int:f_id>/<int:dobj_id>')

class SearchIndexResource(Resource):
    def get(self):
        return ES_INDEX

api.add_resource(SearchIndexResource, '/searchindex')

if __name__ == '__main__':
    app.run(debug=True)
