# The Knowledge Client

This document describes the __Knowledge Client__, and how to use it to build data-powered applications very quickly.

The main goal of the __Knowledge Client__ is to allow users to quickly obtain a high-quality relation, on any topic.  It is intended for integration into applications or data science workflows.  The client obtains its data from the backing [__Universal Knowledge Collaboration Network__](sharingservice.md).  Users may have to consult the __UKCN__ in order to find the right identifiers for data objects and properties.

The current client is written in Python, though there is nothing    Python-specific about it: future clients could be written to integrate with programs in Go, Rust, Swift, etc.

## Data Model
A relation in both the __Knowledge Client__ and the __UKCN__ is akin to a traditional RDBMS relation: it's got rows and columns.  However, our relations differ in two important ways:
1. Each row has a globally-unique identifier. This is roughly similar to the *rowid* that some database systems provide. However, our row ids are globally-unique identifiers.
2. Like a traditional RDBMS, each column has a human-understandable *name* (e.g., "Salary") and a *type* (e.g., "float"). In addition, in our system each column has a *semantic label*. These labels are drawn from a dictionary maintained by the __UKCN__. For example, a column might be annotated by a label */properties/wikidata/P3618*, which indicates "base salary".

## Execution Model
The client allows the programmer to build a single relation at a time.
The sequence of steps that the __Knowledge Client__ performs can be thought of as a single "table initialization step", followed by a series of joins that grow the table's rows and columns.  

Some common kinds of initialization include:
- Creating a table of a single row and a single column. For example, consider a single column that identifies a KG object, with a single row that represents the *Barack Obama* object.
- Creating a table of many rows and a single column. For example, consider a single column that identifies a KG object, with multiple rows that represent members of a class, such as all instances of the *City* object.
- Creating a table that corresponds to a pre-made table in the __UKCN__. For example, the programmer may grab a table of dollar-to-Euro exchange statistics.

After initialization, the user performs a series of joins that potentially add rows and columns to the table. With some naming guidance from the user, the system synthesizes all of the appropriate column metadata for each new row and column.

The system does not try to extract or clean __UKCN__ data at the time of use, apart from a few important exceptions.  At the individual fact level, everything the user sees inside a relation created by the __Knowledge Client__ can be found in the __UKCN__.

The exceptions surround cases when the system believes that facts in the __UKCN__ are correct at the individual level, but will yield a relation that is internally inconsistent.  Unfortunately, this is a well-known problem in knowledge graphs. Consider the example that *Tim Berners-Lee* is an example of *Computer Scientist*, while *Computer Scientist* is an example of *profession*. A __Knowledge Client__ user trying to create a table of professions might inadvertently obtain one that includes *Tim Berners-Lee*.  When appropriate, the __Knowledge Client__ will either silently fix these issues, or will issue a warning to the user.

## Examples

Let's try to show a few examples of using the __Knowledge Client__.

## Tutorial 1: Basic dataset construction with the presidents
__Dinghao, Tian, Kexin: can we add a simple example here?  Just add basic entity data that's already in the knowledge graph.  Presidents, their spouses, and their places and dates of birth. That's it.__


## Tutorial 2: Adding numerical data from the European Union
__Dinghao, Tian, Kexin: here let's add a bit more complicated stuff.  The European Union and GDP data.  Then let's do inflation-adjustment for the GDP data.__

## Tutorial 3: Whole-table functions with National Parks data
__Jenny, let's do the National Parks inception data here, and show how to do whole-table function invocation__.


## REMINDER: WE NEED TO FIGURE OUT THE DATA MODEL DISTINCTION BETWEEN USING WIKIDATA VS USING THE SHARING SERVICE.  RIGHT NOW THE CLIENT ONLY EXPLOITS WIKIDATA, BUT THIS SHOULD CHANGE VERY SOON.
