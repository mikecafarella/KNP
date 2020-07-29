# Specification

## Construct KGPLValue

1. `kgpl.value(val)`  
    Construct a new KGPLValue using val, communicate with server to get the next available id. Reutrn type is KGPLValue class

## Construct KGPLVariable

## Namespace

`prefix: "kg"; namespace: "http://lasagna.eecs.umich.edu:80"`

## Format of nodes

1. ID: URIRef
2. value: Literal(json serialized)
3. kgpl type: URIRef
4. python type: Literal
5. timestamp: URIRef
6. delta update: Literal

## Format of edges

1. hasValue: URIRef
2. kgplType: URIRef
3. pyType: URIRef
4. historyOf: URIRef

## Sharing

current database:
vid     val     timestamp
6       (1,2,3) 1595998318.634551
7       [4,5,6] 1595998375.016583
8       {'gg': 'mt'}    1595998413.149163
9       1999    1595998668.711663
