# KGP Design

This document describes the latest attempt (updated March 5, 2020) for a
KGP design.  It is more concrete and practical than previous efforts. 

The KGP system comprises five primary components:

- The **Raw Knowledge Graph** is a KG such as Wikidata, MusicBrainz,
  or others. It consists of nodes that represent data objects in a
  particular domain, and labeled directed edges that represent named
  properties. Edges always have an entity as a source, and can point
  to an entity or a primitive data value. The Raw Knowledge Graph will
  be continually updated by external social or ML processes. Like all
  KGs, it will be forever somewhat incomplete, incorrect, and
  inconsistent.
- The **Ideal Knowledge Graph** is a cleaned up version of the **Raw
  KG**. It resembles the **Raw KG** with two important exceptions: (1)
  new facts may be added, and (2) all facts have a probability
  attached, reflecting whether the fact is true or not.  Facts that
  are in the **Raw KG** are added to the **Ideal KG** with probability
  1.0.  Producing the **Ideal KG** entails making a number of policy
  decisions around what properties and facts should be added.  Facts
  around __type membership__ are especially important to the **Ideal KG**.
- The **Ideal Codebase** is a set of functions that operate on values
  and types found in the **Ideal KG**.  Each function is
  world-readable and -writeable, much like objects in a public KG.
  The overall contents of the **Ideal Codebase** is likely to change
  continually, as many users add new functions and edit previous
  ones.  Functions in the **Ideal Codebase** are branching programs
  (that is, programs with conditionals but no loops) that
  do not have side effects.  **Ideal Functions** can declare the level
  of probabilistic confidence required to invoke them, but otherwise
  cannot directly access the probabilities associated with its
  inputs.  Each line of code in an **Ideal Function** is one of the
  following:
      1. Another **Ideal Function**
      2. One of a handful of builtin operations
      3. One of a few data-accessor methods defined by the **Ideal
         KG**
      4. A piece of executable code (such as Python) that has been
         adorned with types from the **Ideal KG**.
- The **Invocation Interface** allows a user to specify an **Ideal Function**
  to execute (along with parameters from the **Ideal KG**).  There are
  several possible interfaces:
      1. A browser-based tool for data scientists that employs
         aggressive autocomplete to unambiguously indicate an
         **Ideal Function** and **Ideal KG** parameters.
      2. A voice- or text-based for general users where both **Ideal
         Functions** and **Ideal KG** parameters are indicated in a
         potentially-ambiguous manner. This is akin to modern voice
         assistant usage. In this mode of operation, it will be
         necessary for the system to automatically generate a mapping
         from concrete parameter values to parameter slots in the
         chosen **Ideal Function**.
      3. A more gentle interface for technically-minded
         non-programmers, where **Ideal KG** entities are indicated
         via autocomplete, but **Ideal Functions** are indicated using
         text keywords or some other mechanism.
- An **Executable Program Graph** is produced when an **Ideal Function**
  is executed.  It is a dataflow-style execution graph, in which nodes
  represent function execution, and directed edges represent
  data. Each edge represents a set of data with schema information.
  The system uses a Just-In-Time-style compiler to produce the
  **EPG**.  Since the **Ideal Codebase** is constantly changing, and
  the **Ideal KG** can change at any time, two rapid invocations of the same
  **Ideal Function** could in principle produce quite different
  **EPGs**.

The remainder of this document describes each component in detail.

--------------------------------------------------------

## The Raw Knowledge Graph

This is the easiest part of the system to discuss. It is a real-world
knowledge graph, comprising entity nodes and property edges. Wikidata,
MusicBrainz, and others are popular KGs.

While there are a few great public KGs, unfortunately the tool suite
for constructing novel KGs is not great. The world needs better tools,
so that organizations can build small private versions of
Wikidata-style graphs.  In particular, these tools should replicate
the mechanisms that Wikidata employs to encourage schema convergence
among participants.

We assume the Raw KG will always be incomplete and somewhat
wrong. Also, it will be constantly changing, either via direct user
edits or extraction- and cleaning-style automated mechanisms.

We make one small change to standard KGs to make them more useful:
introducing a **relation** as a primitive data type, so that
properties can point to a dataset.

--------------------------------------------------------

## The Ideal Knowledge Graph

This is a cleaned-up version of the **Raw KG**, produced by an
automatic ML-style mechanism.

The primary goal of the Ideal KG production system is to produce a KG
tht contains facts and properties that are implied by the **Raw KG**,
but not explicitly stated.  For example, it will add to Wikidata the
fact `(Q76, P31, Q82955)`, or in other words, `(Barack_Obama,
instance-of, Politician)`. This fact is implied by various sets and
lists in Wikidata, but is not part of Barack Obama's entity page.

All added facts are adorned with a probability value that indicates
whether or not the fact is true.  Facts imported directly from the
**Raw KG** get a probability of 1.0.  (*This might be a bad idea. What
if we can tell a fact in the Raw KG is false, e.g., it's due to vandalism?*)

An important design decision in constructing the **Ideal KG** is
deciding which properties and facts should be populated. This is a
schema design decision.  For example, should the KG contain just
`spouse-of`, or is it important to contain `wife-of` and `husband-of`
as well?  Should the `born-in` property describe a country, a city, or
a hospital?

For now, I suggest that the the **Ideal KG** process never introduce a
novel property or data object, but rather attempt to emulate the
schema and "fact granularity" decisions of the **Raw KG** as much as
possible.

The quality of the **Ideal KG** is crucial for the success of the
overall system. If it does not present a unified and complete dataset
to **Ideal Functions**, then those functions will be impossible to
write successfully for general use cases.  We will need lots of tools
to instrument how effectively the **Ideal KG** is working when running
programs from the **Ideal Codebase**, and gather as many data quality
signals as possible.

--------------------------------------------------------

## The Ideal Codebase

The **Ideal Codebase** is perhaps the most unusual element of the
overall Knowledge Programming system, and the one where design choices
make the biggest potential difference.

The **Ideal Functions** in this codebase are intended to be the
"executable" analogue of KG entities. That is, they:

- Cover all possible topics
- Embody real-world knowledge, not "software engineering" knowledge
- Incorporate contributions from a large set of poorly-organized
  people
- Are world-readable and -writable, but subject to a social quality
  assurance process.
- Are evergreen functions that are good forever, or close to it. They
  do not need to be modified as the **Raw KG** changes.

### Types

**Ideal Functions** are written using types that are synthesized from
the **Ideal KG**.  Any node in the **Ideal KG** can be treated either
as a data value or as a type, depending on the context in which it is
used.  For example, consider this possible **Ideal Function**:


    GetSpouseDOB(p:  Person): Person {
      return p.spouseOf().dateOfBirth()
    }


In this example, `Person` is used in a type context, both in the input
to the function and in the output.  The set of possible types that a
programmer can use is the set of _all KG nodes_.

During construction of the Ideal KG, the system also constructs all of
the system types.  That is, the system emits a series of tuples of
this form:

    (TypeLabel, testIfDataValueIsMemberOfType(v))


In principle, this could require the Ideal KG to construct tens of
millions of types!  In practice, we can do this lazily: the system
should not actually build a type membership classifier until a
particular TypeLabel is used by a programmer.

The space of types cannot be added to by the programmer.  There is no
such thing as a private type.  All types are either derived from the
KG or are builtins such as __Table__ and __String__.  If the
programmer needs a type that is not in the system, she can add a new
node to the KG.

The methods of the input parameter `p` ---  `spouseOf()` and
`dateOfBirth()` --- are derived from the properties associated with
`Person` in the Ideal KG.  It is OK if a particular instance of
`Person` does not contain the property in question; the synthesized
accessor function simply returns a special value `None`.

It is allowed, but discouraged, for ideal functions to use properties
that are not associated with the type in question. For example, few
examples of `Politician` are ever involved with the US Presidency, so
it is unlikely that the Ideal KG has associated the property
`dateElectedPresident` with the `Politician` type.

However, it may make sense for some pieces of code to nonetheless
execute methods that are not officially "supported" by the type of a
data value.  Consider this function:

    ShowDetailsAboutPresidents(p: Politician):__Table__ {
      return MakeTable("Date Elected", p.dateElectedPresident())
    }

In this case, the code invokes a method that is not officially
supported by the `Politician` type.  However, we imagine the caller
has some special reason to know the input is a President, and has just
used a slightly-incorrect type. That's not perfect, but it is
acceptable.  The correct behavior is for the code to return a value
for values where `dateElectedPresident()` is defined, and `None`
otherwise.  However, the system issues a warning to the author of
`ShowDetailsAboutPresidents()` that the code employs an unsupported
function.

The function signature indicates that it returns a value of type
`__Table__`. The leading and following underscores indicate that this
is a primitive type for the Knowledge Programming system, not one
defined by the Ideal KG.

It is OK to have the same function name, with different type
signatures.  So, for example, it is legitimate to have both of these
in the Ideal Codebase:
`Compare(x: Person, y: Person): __Table__ {}`
and
`Compare(x: TimeSeries, y: TimeSeries): __Image__ {}`

### Type Coercion

In some cases the same method might be parameterized differently.  For
example, a user might write `CompareGDP(USA.gdp, Canada.gdp)` or
`CompareGDP(USA, Canada)`.  In the latter case, the system will
automatically figure out how to translate the parameterized objects
into the intended GDP types.  This translation will be probabilistic
and uncertain; see below for more on probabilities.

As a rule, functions should be written with the "most specific
relevant type".  If you're comparing GDP, then use the GDP type.
Don't use the country type, even if you want to enable calls like
`CompareGDP(USA, Canada)`.  Rely on type coercion for these imperfect
tpye matches.

It is still legal to define `CompareGDP(c1: Country, c2:Country)`. But
in most cases, it's not a good idea if the contents of that method
will simply be implemented as `CompareGDP(c1.gdp(), c2.gdp())`.


### Useful Code

Ideal functions are straight-line programs that can invoke:
1. Other ideal functions
2. Knowledge Graph accessor functions
3. Builtin operators
4. Concrete executable code that has been adorned with types from the
   Ideal KG.


For example, imagine we want to create a plot for time series data:

    PlotTimeSeries(ts: TimeSeries, title: __String__): __Image__ {
      PythonPlotOneLine(ts.getValues(), ts.getTime(), ts.getLabel(), title)
    }

This operates on any Ideal KG value that has been marked as being in
the `TimeSeries` type.  It calls another ideal function, which is
defined as follows:

    PythonPlotOneLine(vals: __Array__, timeVals: __Array__, label:
    __String__, title: __String__):__Image__ {
        return __CallPython__(plot.PlotOneLine(vals, timeVals, label, title)), __Image__)
    }

This method uses the builtin operation `__CallPython__` to calls a
given Python function, mapping parameters to slots in
`plot.PlotOneLine()`. Further, it casts the result of that Python
function to the internal Knowledge Programming type of `__Image__`.

This is a pretty narrow method.  Let's look at something (barely)
more useful.

    CompareTimeSeries(ts1: TimeSeries, ts2: TimeSeries title: __String__): __Image__ {
      PythonPlotTwoLines(ts1.getValues(), ts1.getTime(), ts1.getLabel(),
                         ts2.getValues(), ts1.getTime(), ts2.getLabel(), title)
    }

We can imagine there is another ideal function called
`PythonPlotTwoLines()` that works almost exactly like
`PythonPlotOneLine()`.

So far, so boring.  Let's make it a bit more tailored to a particular
use case:

    CompareGDP(gdp1: GDP, gdp2: GDP): __Image__ {
      __Assert__(gdp1.unit() == gdp2.unit())
      return CompareTimeSeries(gdp1, gdp2, "GDP")
    }


In this case, the code is embodying a small but useful set of
observations about the world:
-- When comparing GDP, it must be true that both values are
   expressed in the same units (e.g., US Dollars)
-- Comparing GDP always means comparing two time series

Now what if the user wants to run `CompareGDP()`, but these facts aren't
true? That brings us to...

### Probabilities

As mentioned in the **Ideal KG** section above, each fact in the Ideal
KG has an attached probability that represents whether the fact is
true.

Each Ideal Function also has a probability that represents whether the
function's _preconditions_ are true.  The preconditions of a function
include:

- Whether the supplied input parameters satisfy the types of the
  method signature.
- Whether the special semantics of any called builtin methods are
  satisfied (such as `__Assert__()`)
- The preconditions of all the called methods

In the case of `CompareGDP()`, the probability that its preconditions
are satisfied is computed over:

- The probability that `gdp1` is an example of type `GDP`.  This is
  embodied in the Ideal KG as the probability value of `(<gdp1>,
  instance-of, GDP)`
- The probability that `gdp2` is an example of type `GDP`.  This
  probability is present in the Ideal KG in the same way.
- The probability that `gdp1.unit()` has the same value as `gdp2.unit()`
- The probability that the preconditions of `CompareTimeSeries()` are
  satisfied when invoked with the parameters here.

Almost any invocation will yield a nonzero probability that its
preconditions are satisfied, but very few of the possible invocations
will yield a large precondition probability.

When a method is invoked there could multiple legitimate methods that
could be chosen for execution. The system will choose the one with the
_maximally-probable preconditions_.

Let's study more about how the Ideal Functions are invoked in the
first place.

--------------------------------------------------------

## The Invocation Interface

How is a Knowledge Program --- that is, a particular parameterized
Ideal Function --- started?  The system can present several possible
interfaces to the user.

### Unambiguous Invocation

The most straightforward is the **unambiguous interface**, intended
for data scientists and developers.  This is essentially the same as
how an Ideal Function invokes another function.  The function name and
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

Every invocation of the Knowlege Programming system entails a small
custom set of KG entities that describe the **execution
environment**.  These values can be used by the Ideal Functions to
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


--------------------------------------------------------

## The Executable Program Graph

This is an executable graph-style program. It is the result of
applying the just-in-time compiler to a particular invocation of an
Ideal Function.

This graph has executable code at each node.  It is primarily a
dataflow graph, but conditionals can be present.  An individual node
might entail looping, but overall the graph structure does not
explicitly represent loops.  (In other words, the graph is acyclic.)
Different runtime environments may get different graphs for an
otherwise-identical function invocation.

The graph that is produced by a single Ideal Function invocation might
be quite different from one produced just moments later by an
identical invocation.  This can be due to changes in the Ideal KG,
changes to the Ideal Codebase, or the execution environment.

The most interesting thing about the **Executable Program Graph** is
that it can help the user find bugs in the Knowledge Program.  If the
user does not like a particular output from the program, she can flag
it to the graph interpreter.  The interpreter has enough metadata to
identify the bug-relevant code and facts from the Ideal Function and
Ideal KG.  This annotation can then be used to either flag a potential
bug in the **Ideal Codebase**, or as distant supervision labels for the
**Ideal KG** construction process, or as social flags to human beings
working on the **Raw KG**.


