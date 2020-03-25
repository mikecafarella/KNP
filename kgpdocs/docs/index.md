# The Knowledge Graph Programming Language

The Knowledge Graph Programming Language, or __KGPL__, is a programming
language that takes Knowledge Graphs as its core data model and
inspiration.

KGPL has a few distinctive qualities:

- __Real World Values and Types__: KGPL covers the "real world" just
  like a Knowledge Graph does. Its enormous standard class library has
  data values and types that reflect the real world: there's a value for
  `Barack_Obama` and one for `Boston_Red_Sox`. There's a type for
  `Politician` and one for `Cartoons`.  These are built using the
  popular Wikidata Knowledge Graph. You can add your own data values
  and types using your own KG. 
- __Run Once, Share Everywhere__: Every KGPL output carries lineage
  information and has a globally-unique URL. That means every program
  output of every execution can be examined, debugged, and extended by
  every other user. 
- __Integration With Data Pipelines__: KGPL assumes its inputs come
  from data pipelines and its outputs will used to feed data
  pipelines. The language makes data quality tracking, debugging, and
  iterative refinement an easy part of every program. 

KGPL also has one __very undistinctive quality__: programs are
basically Python.  Your daily programming habits remain 99% unchanged.
