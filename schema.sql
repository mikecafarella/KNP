CREATE TABLE KGPLValue(
  id TEXT NOT NULL,
  val TEXT NOT NULL,
  lineage TEXT NOT NULL,
  url TEXT NOT NULL,
  annotations TEXT NOT NULL,
  discriminator TEXT NOT NULL,
  KGPLFuncValue TEXT
);

CREATE TABLE Wikimap(
  id TEXT NOT NULL,
  wikiid TEXT NOT NULL
);
