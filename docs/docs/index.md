# The Knowledge Network Programming System

The Knowledge Network Programming System, or __KNPS__, is a programming
system for building knowledge-powered applications. It allows users to more easily use existing knowledge and to curate new knowledge.

It has two main components:

- The __Knowledge Client__ allows users to easily specify a desired relational table, suitable for immediate application use.  Specifying almost any desired table can be done in just a few lines of simple code.  This table
is automatically populated from a comprehensive back-end knowledge graph that includes raw data and data-processing functions on a vast range of topics. In most cases, the user can avoid the typical tedious process of data discovery, marshalling, cleaning, and curation.

- The __Universal Knowledge Collaboration Network__ is the back-end knowledge graph that powers the __Knowledge Client__.  In many ways it is similar to existing knowledge graphs like Wikidata and others: it hosts data, contains entities and properties, offers a variety of query interfaces, can host both well-known objects and unpopular objects, and relies on social processes for scalable curation. The __UKCN__ is distinctive in that it contains a much wider array of datatypes than is typical: in addition to concrete entities, it can contain files, databases, schemas, properties, execution events, functions, and other items. As a result, the contents of the UKCN can model both the "real" world as well as the computational one. 


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
