# Lineage

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
