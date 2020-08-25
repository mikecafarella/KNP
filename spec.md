# Specification

## Construct KGPLValue

```kgpl.value(val, comment)```  
Construct a new KGPLValue given a concrete value `val` and the description about this KGPLValue `comment`, communicate with the server to get the next available id. The return type is KGPLValue class object.

## Load KGPLValue

```kgpl.load_val(vid)```
Load an existing KGPLValue given the id of it `vid`. The return type is KGPLValue class object.

## Construct KGPLVariable

```kgpl.variable(val_id, comment)```
Construct a new KGPLValue given the id of the KGPLvalue `val_id` and the description about this KGPLVariable `comment`, communicate with the server to get the next available id. The return type is KGPLVariable class object.

## Load KGPLVariable

```kgpl.load_var(vid)```
Load an existing KGPLVariable given the id of it `vid`. The return type is KGPLVariable class object.

## Update KGPLVariable

```kgpl.set_var(kg_var, val_id, comment)```
Change the concrete value of an existing KGPLVariable given the KGPLvariable `kg_var`, the id of the value `val_id` and a new description about it, and return the updated kgplVariable. The return type is KGPLVariable class object.

## Member functions of KGPLValue

```kgpl.KGPLValue.getVid()```
Return the url of the KGPLValue.

```kgpl.KGPLValue.getConcreteVal()```
Return the concrete value of the KGPLValue.

## Member functions of KGPLVariable

```kgpl.KGPLVariable.getVid()```
Return the url of the KGPLVariable

```kgpl.KGPLVariable.getConcreteVal()```
Return the KGPLValue of the KGPLVariable. Note that the KGPLVariable in a user's program may not have the latest version of its own if some other users change the KGPLValue it refers to, so the KGPLValue this method returns is what the KGPLVariable refers to in this user's probram, which may not be the same as latest version of the KGPLVariable.

```kgpl.KGPLVariable.getLatest()```
Refresh the version of KGPLVariable so that the KGPLVariable in the user's program has the latest version.

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
6. hasComment: URIRef `kg:hasComment`

## Database
1. 
![Alt text](outdated/database.png?raw=true "Title")
