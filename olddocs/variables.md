# Variables

KGPL variables are named objects that refer to a particular KGPL value
at any given point in time.

The variable's `id` field is a universally-unique identifier for all
time and space.  This never changes.

The `current-value` field is the `id` of a KGPL value.  This can be
changed over time

The `owner` field indicates the username of the owner of the
variable. This is important for determining who is allowed to modify a
variable.

The `url` field is optional. It is populated when the variable is
registered with a __KGPL sharing service__. The URL syntactically
contains the variable's `id`. When a __KGPL sharing service__ is
queried using this URL, it will return all of the variable's other
fields.

Note that in principle, a variable could be shared and widely known,
but its value could be more limited.  This might be appropriate in
certain information-sharing scenarios; for example, the government
knows that there is a precomputed monthly unemployment number, but
this number is not widely revealed until a particular time and date.

The `annotations` field is arbitrary human-readable information that
can be added to the variable. It is carried along with the variable,
but has no practical impact on its programmatic KGPL usage.  It could
have an impact on the findability or usefulness of the variable for
other human beings. For example, there might be a search service that
allows users to find useful variables on an existing __KGPL sharing
service__. This search service might use the annotations field to get
better search results.

When a registered variable is changed, the update should be
immediately transmitted to its registered sharing service.


You can observe all of the KGPL variable fields --- and those of its
current value --- at the Python REPL:
```
>>> import kgpl
>>> from kgpl import kgplSquare
>>> from kgpl import KGPLVariable
>>>
>>> x = KGPLVariable(kgplSquare(3))
>>> x
id: 8cf28bb1-ea67-4c37-a949-7d8bab2be6f8
owner: michjc
url: <unregistered>
annotations: []
current-value: 9
>>>
>>> x.currentvalue
concrete-value: 9
id: 01f9da67-9206-499f-a985-30d734ffbbef
lineage: <kgpl.Lineage object at 0x101338588>
url: <unregistered>
annotations: []
>>>
>>> x.reassign(kgplSquare(4))
>>> x
id: 8cf28bb1-ea67-4c37-a949-7d8bab2be6f8
owner: michjc
url: <unregistered>
annotations: []
current-value: 16
>>>
>>> x.currentvalue
concrete-value: 16
id: 2ac5abea-e790-4100-828c-39f3637e9bc5
lineage: <kgpl.Lineage object at 0x101417080>
url: <unregistered>
annotations: []
```

## Relationship to Knowledge Graph Entities

An object in an extant knowledge graph, such as Wikidata, can be
viewed as a registered KGPL variable.  For example, the Barack Obama
URL at Wikidata (Q76) is a uniquely-identified variable that refers at
any point in time to a particular value. That value has the __Entity__
type.

Most KGPL variables will never be registered. Most registered ones
will never become well-known. But a small fraction will become
well-known and potentially used by many. The current KGs can be
thought of as sets of registered and well-known KGPL variables.


## Updates

A KGPL variable can be updated whenever its owner decides it is
appropriate.  Some KGPL variables will be updated by social mechanisms
-- basically, whenever a human wants to, the variable gets updated.
   Some will be updated according to a regular schedule, such as a
   variable that reflects a stock price, which gets updated every
   minute.  Some will be updated according to external events, such as
   a temperature sensor reading.  This update policy should be
   described in the human-readable part of a well-known variable.

A KGPL variable can be updated by a process that is external to the
KGPL universe.  That is, external actors (social software, data feeds,
etc) can publish variables "into" the KGPL variable space.

But much of the time, a KGPL variable is updated because a KGPL
program runs and changes the value.  That's great!

KGPL programs can register interest in their upstream variables. When
the upstream variable is modified, the KGPL program may decide to
re-execute.

## Permissions

KGPL variables are owned by a single user and registered at a single
service.  Unlike values, variables have a "home service".  That
service might be an internet-wide one, or limited to a particular
group.

Unlike value sharing, sharing a previously-private variable with an
external party can only be done via changing access control to the
home sharing service.  Variables cannot be transmitted between sharing
services.

