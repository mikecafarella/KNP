# KGPL Sharing Services

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

