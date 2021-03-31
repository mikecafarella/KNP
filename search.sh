curl "localhost:9200/_cat/indices?v=true"
curl -H "Content-Type: application/json" -XPOST "localhost:9200/bank/_bulk?pretty&refresh" --data-binary "@accounts.json"
curl -H "Content-Type: application/json" -XPOST "localhost:9200/kgpl/_bulk?pretty&refresh" --data-binary "@kgpl_hand.json"
curl -XPOST 'localhost:9200/logs/my_app' -H 'Content-Type: application/json' -d'
{
	"timestamp": "2018-01-24 12:34:56",
	"message": "User logged in",
	"user_id": 4,
	"admin": false
}
'


curl -H "Content-Type: application/json" -XPOST "localhost:9200/bank/_bulk?pretty&refresh" --data-binary "@accounts.json"

curl -XGET 'localhost:9200/bank/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "address": "mill lane" } }
}'


curl -H "Content-Type: application/json" -XPOST "localhost:9200/kgpltest/_bulk?pretty&refresh" --data-binary "@kgpl_hand.json"

curl -H "Content-Type: application/json" -XPOST "localhost:9200/kgpltest2/_bulk?pretty&refresh" --data-binary "@zjy.json"


curl -XPOST 'localhost:9200/kgpltest/_doc/3' -H 'Content-Type: application/json' -d'
{
    "@id": "http://127.0.0.1:5000/val/0",
    "http://127.0.0.1:5000/belongTo": [
        {
            "@value": "anonymous"
        }
    ],
    "http://127.0.0.1:5000/hasComment": [
        {
            "@value": "function for Relation"
        }
    ],
    "http://127.0.0.1:5000/hasValue": [
        {
            "@value": "{\"types\": [\"gANja25wcy5PUk1fY2xpZW50ClJlbGF0aW9uCnEALg==\"], \"__funcwithsig__\": true, \"code\": \"4wEAAAAAAAAAAQAAAAcAAABDAAAAc2IAAAB8AGoAZAFkAmQDZARkAmQFjQUBAHwAagFkBoMBAQB8AGoAZAdkCGQJZAJkCo0EAQB8AGoAZAtkCGQMZAJkCo0EAQB8AGoAZA1kCGQOZAJkCo0EAQB8AGoCgwABAHwAagNTACkPTloDUDM5VFoJUHJlc2lkZW506RQAAAApAtoFbGltaXTaBWxhYmVsWg1QcmVzaWRlbnRfUDM5WgNQMjZGWgZTcG91c2UpAXIDAAAAWgRQNTY5Wg1kYXRlX29mX2JpcnRoWgNQMTlaDlBsYWNlX29mX2JpcnRoKQTaBmV4dGVuZNoLY2hhbmdlRm9jdXPaBXF1ZXJ52gJkZikB2gFyqQByCQAAAPoePGlweXRob24taW5wdXQtMi01Y2M2MDFiNGM3Nzk+2gVteWZ1bgIAAABzDgAAAAABFAEKARIBEgESAQgB\", \"defaults\": \"gANOLg==\", \"closure\": \"gANOLg==\"}"
        }
    ],
    "http://127.0.0.1:5000/kgplType": [
        {
            "@id": "http://127.0.0.1:5000/kgplValue"
        }
    ],
    "http://127.0.0.1:5000/pyType": [
        {
            "@value": "FunctionWithSignature"
        }
    ]
}
'


curl -XPOST 'localhost:9200/kgpl/_doc/1' -H 'Content-Type: application/json' -d '
{"url": "http://127.0.0.1:5000/val/1", "owner": "anonymous", "comment": "function for Relation", "pytype": "FunctionWithSignature"}
'

curl -XPOST 'localhost:9200/kgpl/_doc/2' -H 'Content-Type: application/json' -d '
{"url": "http://127.0.0.1:5000/val/2", "owner": "alice", "comment": "test publish", "pytype": "Int"}
'

curl -XPOST 'localhost:9200/kgpltest2/_doc/3' -H 'Content-Type: application/json' -d '
{"url": "http://127.0.0.1:5000/val/0", "owner": "anonymous", "comment": "function for Relation", "pytype": "FunctionWithSignature"}
'

curl -XGET 'localhost:9200/bank/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "address": "mill lane" } }
}'

curl -XGET 'localhost:9200/kgpltest2/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} }
}'

curl -XGET 'localhost:9200/kgpltest2/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "comment": "publish" } }
}'

curl -H "Content-Type: application/json" -XPOST "localhost:9200/kgpl3/_bulk?pretty&refresh" --data-binary "@zjy.json"

curl -XGET 'localhost:9200/kgpl3/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "comment": "Quility" } }
}' > zjyout.json

curl -XGET 'localhost:9200/kgpl3/_search' -H 'Content-Type: application/json' -d'
{
  "query": { "match": { "comment": "Quility employee" } }
}' > zjyout.json


curl -XGET 'localhost:9200/kgpl3/_search' -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "comment": {
        "query": "Qility",
        "fuzziness": "AUTO"
      }
    }
  }
}' > zjyout.json

curl -X GET 'localhost:9200/kgpl/_search' -H 'Content-Type: application/json' -d'
{
  "query": {
    "multi_match": {
        "query": "Jiayun",
        "fields": [ "url", "comment", "owner", "pytype" ] 
    }
  }
}' > zjyout.json


curl -XDELETE localhost:9200/index/type/documentID
