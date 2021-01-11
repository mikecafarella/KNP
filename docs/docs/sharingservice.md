# The Univeral Knowledge Collaboration Network

The __UKCN__ is a knowledge graph that is similar to other Wikidata-style knowledge graphs. Like existing systems, it:
- Hosts data
- Contains entities and properties
- Offers a range of query interfaces, such as SPARQL and the __Knowledge Client__
- Hosts both well-known objects (e.g., Barack Obama) and obscure ones (e.g., a random uploaded image file)
- Largely relies on social processes for data curation

Unlike existing systems, the __UKCN__ also models the computational world, with support for storing files, databases, schemas, execution events, functions, and other items. This allows the __UKCN__ to apply the virtues of traditional knowledge graph systems --- topic flexibility and efficient curation --- to all the data that an application developer might need.

## Using the UKCN
Like Wikidata, the __UKCN__ presents an HTML browser interface for users.  Anyone can search and retrieve data from the __UKCN__.  With an account, a user can create new __UKCN__ objects, annotate and edit existing ones, run functions, and carry out a range of other tasks.

Every data object in the __UKCN__ has its own URL. This URL can be used in the browser to find an object. The same URL can be provided to the __Knowledge Client__ for various use cases.  Sharing data with a colleague is as easy as sharing a webpage: just send your friend the appropriate URL.

Every data object in the __UKCN__ has an affiliated user account as its owner. In the current version of the __UKCN__, all data objects are world-readable and world-writable. Future versions will implement user permissions that prevent unauthorized access and edits.

## Data Model
Data objects in __UKCN__ are immutable: with one important exception, they can never change and are never deleted.

Every immutable data object has an *obscure identifier*. This can be used to fetch the data object, forever. Because *obscure identifers* are never recycled, and because data objects can never be modified, __UKCN__ can be used for long-term provenance tracking.  An object with an obscure identifier is akin to a particular version of a particular entity in Wikidata; it might be useful and popular, but probably not.

The __UKCN__ also offers *well-known identifiers*. This is the only kind of value in the __UKCN__ that can change over time.  A well-known identifier starts with the letter 'X', followed by an integer.  It is akin to the set of top-level entities in Wikidata, such as Q76 (Barack Obama).

A well-known identifier always points to a single immutable data object (which, of course, also has an obscure identifier).  This is similar to the way in which a high-level Wikidata identifier (e.g, Q76) at any moment in time points to a particular version of the entity.

In practice, users can mostly ignore this distinction. Most people will mostly deal with *well-known* objects; that is, objects currently pointed-to by a *well-known identifier*.  Non-well-known objects are generally only of interest when looking at past versions (e.g., for provenance tracking reasons).

Users retrieving __UKCN__ objects using a single query interface, whether its via an obscure identifier or a well-known identifier, 

## Deployment
There is a single __UKCN__ that is implemented across multiple servers, in the same way there is a single World Wide Web implemented across multiple web servers.  This will allow users and institutions to host data that might be tied to a particular location, while allowing users to ignore physical placement when annotating and curating data.

However, the current __UKCN__ software implements only "single-server mode".

## Interfaces
The __UKCN__ allows users to access it in three ways:
1. When building applications, via the __Knowledge Client__
2. When curating and sharing data, via the HTML Browser interface
3. When uploading novel data artifacts programmatically, via the REST API

This last interface is primarily useful when integrating the __UKCN__ with existing data pipelines.

## Getting Started
Go here to install and run the __UKCN__ system.







<!--

# Obsolete Text
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

-->

