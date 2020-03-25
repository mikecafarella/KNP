# Introduction to KGPL

KGPL stands for the Knowledge Graph Programming Language.  It takes
knowledge graphs like Wikidata as inspiration for its unique approach
to types, code sharing, and reusability.

Here are a few of the qualities that make KGPL distinctive:
- KGPL knows about the "real world" via Knowledge Graph entities and
  types
- Data sharing is a first class part of KGPL
- KGPL assumes data quality is imperfect and iterative refinement is
  always part of the development process

# Values

A value in KGPL contains several fields.

The `concrete-value` field can be one of:
- A Python value
- An Entity. This is a special type designed to model the Wikidata KG
  entity model. It has properties and values.  The property labels may
  be annotated with a label from a shared namespace.
- A builtin KGPL type, such as __Image__, __Relation__, or several
  others.

The `id` field is a universally-unique identifier.  It is akin to a
UUID or GUID, but since we need one for every value in every execution
of a KGPL program, we likely need more bits than previous UUID
standards.

The `lineage` field describes how the value was computed. It is a
directed graph that describes the unique values and function that were
used to compute this value.

The `url` field is optional. It is populated when the value is
"registered" with a __KGPL sharing service__. The URL syntactically
contains the `id`. When a __KGPL sharing service__ is queried using this URL, it
will return all of the other fields.

The `annotations` field is arbitrary human-readable information that
can be added to the value. It is carried along with the value, but has
no practical impact on its usage.

A value is created once and can never be edited. As a result, a
registered value never needs to be edited.


## Sharing

Values can be shared between programs or users via simply sharing the
URL. As a result, before a value can be shared it must be registered
at the __KGPL service__.

When a value is shared, the URL and its lineage is always
available to the consumer. This means every KGPL program output can be
examined for how it was computed. This is helpful for
sharing datasets in a scientific, engineering, or policy context.


## Lineage 

A value's lineage is a directed tree that describes how the value was
computed. A value node is annotated with its `id` or its
`url`. Functions in KGPL always generate a special value of type
__Execution__. This value contains a special field that identifies the
`source-function` that generated it, along with an optional `log`
message generated during execution.

Values with a `url` can always have their details looked up at a
__KGPL sharing service__. As a result, the lineage tree does not have to be
fully-materialized; nodes with a `url` field just can be referred to
and do not need to store further back history.  This allows lineage
trees, which might be quite large, to be made more compact.

There is a single internet-wide KGPL service that will exist as soon
as the language starts running.


## Permissions

Values do not have access control. They simply exist. In most cases,
the best way to keep a value secret from someone is to not share it
with that person.

But in many cases scoped sharing would be useful. For example, people
inside an organization want to be able to share data internally, but
not with external people or with an external central service.

It is therefore possible to run a __private KGPL sharing service__.
This service is not visible to all users in the universe. Controlling
access to this service is outside the scope of KGPL.  Just treat the
private KGPL service like an intranet URL.

A single value might have a lineage tree that refers to several KGPL
sharing services. Consider a company that publishes a `profits` value,
based on substantial amounts of internal data. The profits quantity,
and its method of computation, should be public but the raw data
should be private. In this case, external users of the value would be
able to observe its lineage up to the point where it relied on private
data.

In some cases, organizations might want to publicly share
previously-secret values.  Or they might want to temporarily share
private data with an external governmental organization.  In all of
these cases, the `id` field stays stable.  Sharing this private data
entails simply re-registering the entire lineage chain with an
external service.

Because values can never change, sharing a value with another service
is always safe to do, with no version control problems.  A service can
simply union its current set of known values with all the values it
ever hears about.


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


# Types

As mentioned above, concrete values can be Python values, KG Entities,
or an instance of one of several builtin KGPL types, such as
__Image__, __Relation__, or others.

KGPL also includes a large "Core KGPL Type Library".  This library
has thousands of types. KGPL Entities and __Relation__ values may fall
into zero or more of these types. The types are meant to describe
useful classes of values, such as:

- Politicians
- Countries
- GDP Data
- HeartDiseaseData
- and many others

A type in KGPL is a value that is treated in certain special
ways. Its `concrete-value` field is a tuple of two fields:
- `typename` is a URL-style human-understandable label that describes
  the intended type. 
- `typefunc` is a function that takes as an argument a single
  parameter: any KGPL value. It returns a probability that determines
  whether the given argument is a "member" of the type.

The exact set of types in the KGPL type library will change over time,
but the intention is for it to be general-purpose and comprehensive.

The KGPL Hierarchical Namespace is a URI-style manner of naming types.
The core types are named as `/core/<typelabel>`, like
`/core/Politician`, `/core/GDPData`, and so on.

Users can add new types by creating new `(typename, typefunc)` pairs
and registering them with an accessible __KGPL Sharing Service__.
The desired namespace for user-registered types is not entirely clear,
but should be something like `/users/mcafarella/Recipe` or
`/mit.edu/Lab`.

In the core library, the intention is for most type-detection
functions to be machine-learned artifacts, but there is nothing that
requires this.  It might especially make sense for users to define
types algorithmically.


# Functions
A function is a piece of executable code.  A function is another kind
of value.  It can be created, but not edited, destroyed, or versioned.

When a function is executed, it yields the standard results (that is
values), as well as an __Execution__ value.  This value encapsulates
the execution event via three fields. The `source-function` field is
the identifier of the value that represents the function that was
executed.  The `timestamp` value simply indicates when the function
was run. The `log` value indicates any information emitted by the
function during execution.

Some of the nodes in a value's directed lineage tree are __Execution__
values. 

Like other values, a function can be assigned to a variable.  That
variable can change its value over time, like any other variable.  It
might be shared, become well-known, etc.

A function value is fixed, but most of the time when programming or
sharing with others, users refer to functions via a variable name.

Since type membership is probabilistic, it is possible that a single
function invocation may satisfy multiple functions simultaneously.  In
these cases, the system will invoke the maximally-probable function.


# Program Code

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


# Interfaces

How is a KGPL function started?  The system can present several possible
interfaces to the user.

### Unambiguous Invocation

The most straightforward is the **unambiguous interface**, intended
for data scientists and developers.  This is essentially the same as
how an KGPL function invokes another function.  The function name and
its parameters are unambiguously indicated by the user's code.  The only
ambiguity around which method is invoked is driven by
identically-named functions with different type signatures.

### Method-Ambiguous Invocation

Slightly more user-friendly is the **method-ambiguous interface**,
in which parameters and their order are indicated entirely
unambigously, but the method name is indicated via text keywords.

In this scenario, we can imagine that the chosen function is given an
additional "virtual precondition" that tests whether the candidate
function was indicated by the user's set of keywords.  This can be
quantified with a probability.

### Implicit Invocation

Finally, the most user-friendly input mode is one in which the
function, its parameters, and their order are given by the user
entirely via a text-style or voice-driven interface.  Again, the
interface adds a virtual precondition that measures whether the
method, the identified parameter values, AND the mapping from values
to slots were all indeed intended by the user.

### Execution Environments

Every invocation of a KGPL function entails a small
custom set of KG entities that describe the **execution
environment**.  These values can be used by a function to
control output depending on the execution environment.

For example, the same code might be runnable either on a laptop with a
large screen, or in voice mode.  If the system returns a table, it
might make sense to present the entire result on a scrollable laptop
screen, but in a voice setting it would only make sense to read the
first tuple aloud.  How can this be implemented?

    RenderTable(t: __Table__): __Table__ {
      if (__Environment__.isVoiceOnly) {
        return t[0]
      } else {
        return t
      }
    }

The conditional statement overall always has a precondition
probability of 1.  One particular branch has a precondition
probability that depends on whether its tested condition is true (or,
for the else branch, (1-p)).

### Managing Uncertainty Thresholds

In some cases, the precondition probability is useful for comparing
different alternatives.  The user might have invoked `Compare(x, y)`;
depending on the values for `x` and `y`, either `Compare(x: Person,
y:Person)` or `Compare(x: TimeSeries, y: TimeSeries)` might be more
probable.

But what should be done when the precondition probability of the
maximally-probable option is still quite low?  The right course of
action depends on the environment and context. For example, the
unambiguous interface probably should always run whatever the user
asks for, while the implicit invocation interface should probably only
run code when the confidence is above a certain threshold.

Each invocation interface can register two special values: the minimum
probability for function execution, and the minimum probability for
warning the user prior to function execution.

Finally, there is the probability associated with conditionals.  The
__True__ branch is always evaluated when its probability is 95% or
higher.





- __Run Once, Debug Everywhere__: It is easy to share, examine,
  discuss, copy, and modify single executions.
- __The Universal Class Library__: KGPL offers a class library of more
  than __70 million__ individual and easily-understood types. These
  types reflect real-world categories, such as Presidents, Buildings,
  Emotions, Satellites, and many more
- __Easy Fine-Grained Code Sharing__: KGPL makes it easy to share
  even individual variables with other programs.
- __Practical Python__: Despite all of the above features, KGPL looks and
  feels like Python 99% of the time

