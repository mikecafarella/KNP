# Specification

## Construct KGPLValue

`kgpl.value(val)`  
Construct a new KGPLValue given a concrete value `val`, communicate with the server to get the next available id. The return type is KGPLValue class object.

## Load KGPLValue

`kgpl.load_val(vid)`
Load an existing KGPLValue given the id of it `vid`. The return type is KGPLValue class object.

## Construct KGPLVariable

`kgpl.variable(val_id)`
Construct a new KGPLValue given the id of the concrete value `val_id`, communicate with the server to get the next available id. The return type is KGPLVariable class object.

## Load KGPLVariable

`kgpl.load_var(vid)`
Load an existing KGPLVariable given the id of it `vid`. The return type is KGPLVariable class object.

## Update KGPLVariable

`kgpl.set_var(vid,val_id)`
Change the concrete value of an existing KGPLVariable given the id of the variable `vid` and the id of the value `val_id` and return the updated kgplVariable. The return type is KGPLVariable class object.

## Namespace

`prefix: "kg"; namespace: "http://lasagna.eecs.umich.edu:80"`

## Format of nodes

1. ID: URIRef `kg:<id>`
2. value: Literal(json serialized)
3. kgpl type: URIRef `kg:kgplValue` or `kg:kgplVariable`
4. python type: Literal
5. timestamp: URIRef `kg:<timestamp>`
6. delta update: Literal

## Format of edges

1. hasValue: URIRef `kg:hasValue`
2. kgplType: URIRef `kg:kgplType`
3. pyType: URIRef `kg:pyType`
4. historyOf: URIRef `kg:historyOf`
5. pointsTo: URIRef `kg:pointsTo`

## Database

![Alt text](database.png?raw=true "Title")

## Sharing

current database:
vid     val     timestamp
6       (1,2,3) 1595998318.634551
7       [4,5,6] 1595998375.016583
8       {'gg': 'mt'}    1595998413.149163
9       1999    1595998668.711663
