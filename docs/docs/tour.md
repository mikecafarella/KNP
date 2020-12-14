# A Tour of KGPL

Here is a whirlwind tour of KGPL!

## Values

A __value__ in KGPL contains several subfields.

The `concrete-value` field is the standard value you actually want to
process and use. It can be one of:

- A Python value
- An `Entity`. This is a special type designed to model the Wikidata KG
  entity model. It has properties and values.  The property labels may
  be annotated with a label from a shared namespace.
- A `Relation`. This is a data table with a schema of property names.


The `id` field is a universally-unique identifier.  It is akin to a
UUID or GUID, but since we need one for every value in every execution
of a KGPL program, we likely need more bits than previous UUID
standards.

The `lineage` field describes how the value was computed. It is a
directed graph that describes the unique values and function that were
used to compute this value.  ([Read more about lineage](lineage.md),
if you like.) 

The `url` field is populated only after the value is "registered" with
a [KGPL sharing service](sharingservice.md). The `url` field, if
populated, always syntactically contains the `id` (so if you have the
`url`, you can derive the `id`). When a value is registered with a
KGPL sharing service, that service can always return all of the
value's fields.

The `annotations` field is arbitrary human-readable information that
can be added to the value. It is carried along with the value, but has
no practical impact on its usage.

A value is created once and can never be edited. As a result, a
registered value never needs to be edited.

Values can be shared between programs or users via simply sharing the
URL. As a result, before a value can be shared it must be registered
at a KGPL sharing service. When a value is shared, the URL and its lineage is always
available to the consumer. This means every KGPL program output can be
examined for how it was computed. This is helpful for
sharing datasets in a scientific, engineering, or policy context.

You can observe all of the KGPL value fields at the Python REPL:
```
>>> import kgpl
>>> from kgpl import kgplSquare
>>> kgplSquare(3)
concrete-value: 9
id: 0051051e-6e0e-11ea-b7d5-8c859062bac5
lineage: <kgpl.Lineage object at 0x10cd02470>
url: <unregistered>
annotations: []
```



## Variables

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
registered with a [KGPL sharing service](sharingservice.md). The URL syntactically
contains the variable's `id`. When a KGPL sharing service is
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
allows users to find useful variables on an existing KGPL sharing
service. This search service might use the annotations field to get
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

Variables are pretty rich objects in KGPL.  [You can read more about
them here](variables.md).


## Types

KGPL includes a large general-purpose type library.  This library
has __thousands__ of types and is meant to cover most "real world"
concepts. KGPL Entity and Relation values may fall into zero or more
of these types. The types are meant to describe useful classes of
values, such as: 

- `Politicians`
- `Countries`
- `GDPData`
- `HeartDiseaseData`
- and many others

The exact set of types in the KGPL type library will change over time,
but the intention is for it to be general-purpose and comprehensive.

The KGPL type namespace is a URI-style manner of naming types.
The core types are named as `/core/<typelabel>`, like
`/core/Politician`, `/core/GDPData`, and so on.

You use a KGPL type in Python code like this:

```
def computeElectoralWinRatio(p: /core/Politician):
  winCount = 0
  totalElections = 0
  for election, didWin in p.elections:
    totalElections += 1
    if didWin:
      winCount += 1

  return winCount / float(totalElections)
```  


A type in KGPL is a value that is treated in certain special
ways. Its `concrete-value` field is a tuple of two fields:

- `typename` is a URL-style human-understandable label that describes
  the intended type. 
- `typefunc` is a function that takes as an argument a single
  parameter: any KGPL value. It returns a probability that determines
  whether the given argument is a "member" of the type.


Users can add new types by creating new `(typename, typefunc)` pairs
and registering them with an accessible [KGPL Sharing Service](sharingservice.md).
The desired namespace for user-registered types is not yet entirely clear,
but should be something like `/users/mcafarella/Recipe` or
`/umich.edu/College` or `/mit.edu/Lab`.

In the core library, the intention is for most type-detection
functions to be machine-learned artifacts, but there is nothing that
requires this.  It might especially make sense for users to define
types algorithmically.


## Functions
A function is a piece of executable code.  A function is another kind
of value.  Like a value, it can be created, but not edited, destroyed,
or versioned. 

When a function is executed, it yields the standard results (that is
values), as well as an __Execution__ value.  This value encapsulates
the execution event via three fields:

- The `source-function` field is the identifier of the value that
  represents the function that was executed.
- The `timestamp` value simply indicates when the function
was run.
- The `log` value indicates any information emitted by the
function during execution.

Some of the nodes in a value's directed lineage tree are __Execution__
values. 

Like other values, a function can be assigned to a variable.  This is
how a function is named.  That variable can change its value over
time, like any other variable.  It might be shared, become well-known,
and so on.

A function value is fixed, but most of the time when programming or
sharing with others, users refer to a function via a variable name.

Since type membership is probabilistic, it is possible that a single
function invocation may satisfy multiple functions simultaneously.  In
these cases, the system will invoke the maximally-probable function.


## Code
The body of a KGPL Function is simply Python code, with a few minor
differences:

- The function signature must declare types for all of its input
  parameters. These can include KGPL Types.
- Function inputs are KGPL variables.  
- The function will be executed in a VM-style environment that will be
  destroyed immediately after execution, so the programmer cannot rely
  on retaining side effects.  All important results must be returned
  by the function call.
- The function must create KGPL-style results to be returned. In
  particular, it must create an __Execution__ value and appropriate
  KGPL-style values (with unique identifiers and lineage) for all
  returned items.

Building an accurate lineage graph for each output value can be
burdensome. If the function's outputs are created using special KGPL
helper functions, this output lineage graph will be generated
automatically.


## Sharing
KGPL enables easy __value sharing__ and __variable sharing__.  Both
require the use of a __KGPL sharing service__.

In order to share a value with another user or program, a KGPL runtime
must:

1. Register the value(s) with a KGPL sharing service. The runtime
   transmits all the relevant data to the service. The service replies
   with a URL.
2. Retain the URL, which can be forwarded to external users or
   programs.
3. Be aware that the KGPL sharing service may replicate the value and
   share with other KGPL services.

Registering a variable is much the same, with two important differences:

1. A KGPL sharing service cannot replicate a variable with other
   services. A registered variable lives on a single service.
2. A KGPL sharing service must enforce variable ownership access
   control. Only the owner of a variable is allowed to update its
   value in the future.   


## Interfaces
How is a KGPL function started by a user?  Several possible interfaces
are available.

### Unambiguous Invocation

The most straightforward is the **unambiguous interface**, intended
for data scientists and developers.  This is how one KGPL function
invokes another.  The function name and
its parameters are unambiguously indicated by the user's code.  The only
ambiguity around which method is invoked is driven by
identically-named functions with different type signatures.

### Method-Ambiguous Invocation

Slightly more user-friendly is the **method-ambiguous interface**,
in which parameters and their order are indicated entirely
unambiguously, but the method name is indicated via text keywords.
This might be appropriate in a search-style ranking interface.

### Implicit Invocation

Finally, the most user-friendly input mode is one in which the
function, its parameters, and their order are given by the user
entirely via a text-style or voice-driven interface.


## Tools
The KGPL system includes several pieces of code and data:

1. The KGPL core type and variable library. These are types and variables
   that are globally accessible. They are shared at the "root" KGPL
   sharing service.
2. Python libraries that implement the type, variable, and value
   systems.
3. A sharing service runtime binary that can be downloaded and executed by
   anyone.
4. A "root" sharing service that runs that binary and is always
   available to all KGPL users.    










