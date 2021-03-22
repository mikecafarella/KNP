Sample documents from CORD-19-related datasets to illustrate a use case for KNPS

The shared key between the various datasets is the 40-character hash, e.g. 44efd15ada8c6e6a9de4017402163286a4b06905

Datasets:

  metadata.csv - Primarily a list of IDs linking the document to other catalogs: PMC, ArXiv, DOI

  pdfs - The source PDF document

  parses - Structured text data parsed from the PDF. Text is organized into paragraph-level blocks.
           Within each block, spans identify other structural elements (figures, bibliography entries)

  segmentation - Structured text data derived from the "parses" dataset. Text is organized into a single block.
                 Within the block, spans identify sentence boundaries.


Use cases:
  There is replication of data between the datasets, which we'd rather avoid. The producer of the "segmentation" data
  probably choose to replicate the text data because they did not trust that the identifier would remain stable.

  Imagine a slightly different segmentation dataset, where spans identify entities and are given IDs into
  a catalog of entities. Then interesting queries would be to identify the set of papers that mention some set of entities,
  filtered by some criteria from other catalogs, like MeSH terms from PMC.

  For a list of real-life community-provided annotations on CORD-19, see https://github.com/w3c/hcls/wiki/CORD-19-Semantic-Annotation-Projects

  
