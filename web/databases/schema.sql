CREATE TABLE IF NOT EXISTS results(
    rid integer primary key AUTOINCREMENT,
    kpid integer not null,
    method text,
    KG text,
    KNP_version text,
    result_img blob,
    result_text text,
    rank integer,
    FOREIGN KEY(kpid) REFERENCES knowledge_programs(kpid)
);

CREATE TABLE IF NOT EXISTS knowledge_programs(
    kpid integer primary key AUTOINCREMENT,
    program text
);