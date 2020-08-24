# Specification

## Construct KGPLValue

`kgpl.value(val, comment)`  
Construct a new KGPLValue given a concrete value `val` and the description for it `comment`, communicate with the server to get the next available id. The return type is KGPLValue class object.

## Load KGPLValue

`kgpl.load_val(vid, comment)`
Load an existing KGPLValue given the id of it `vid` and the description for it `comment`. The return type is KGPLValue class object.

## Member functions of KGPLValue object

`kgpl.set_val(kg_val, val)`
Change the concrete value of an existing KGPLValue given the kgplValue `kg_val` and the value `val`.

We didn't do delta update. (Confused) We saved the snapshot of the value everytime it changes.

## Construct KGPLVariable

`kgpl.variable(val_id)`
Construct a new KGPLValue given the id of the concrete value `val_id`, communicate with the server to get the next available id. The return type is KGPLVariable class object.

## Load KGPLVariable

`kgpl.load_var(vid)`
Load an existing KGPLVariable given the id of it `vid`. The return type is KGPLVariable class object.

## Update KGPLVariable

`kgpl.set_var(kg_var,val_id)`
Change the concrete value of an existing KGPLVariable given the variable `kg_var` and the id of the value `val_id` and return the updated kgplVariable. The return type is KGPLVariable class object.

## Workflow

![Alt text](workflow.png?raw=true "Title")

## Namespace

`prefix: "kg"; namespace: "http://lasagna.eecs.umich.edu:80"`

## Format of nodes

1. ID: URIRef `kg:<id>`
2. value: Literal(json serialized)
3. kgpl type: URIRef `kg:kgplValue` or `kg:kgplVariable`
4. python type: Literal
5. timestamp: URIRef `kg:<timestamp>`

## Format of edges

1. hasValue: URIRef `kg:hasValue`
2. kgplType: URIRef `kg:kgplType`
3. pyType: URIRef `kg:pyType`
4. hasHistory: URIRef `kg:hasHistory`
5. hasKGPLValue: URIRef `kg:hasKGPLValue`

## Database
1. 
![Alt text](database.png?raw=true "Title")
