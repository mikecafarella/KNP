CREATE TABLE IF NOT EXISTS results(
    rid integer primary key AUTOINCREMENT,
    kpid integer not null,
    method_name text,
    mapping text,
    parameter_transformers text,
    result_img blob,
    result_text text,
    rank integer not null,
    status integer,
    type text,
    FOREIGN KEY(kpid) REFERENCES knowledge_programs(kpid)
);

CREATE TABLE IF NOT EXISTS knowledge_programs(
    kpid integer primary key AUTOINCREMENT,
    user_code text,
    KG text,
    KNP_version text,
    KG_params text,
    action text
);

CREATE TABLE IF NOT EXISTS Refinements(
    refinement_name text primary key
);

CREATE TABLE IF NOT EXISTS Constraints(
    refinement_name text,
    constraint_name text primary key,
    FOREIGN KEY(refinement_name) REFERENCES Refinements(refinement_name)
);

CREATE TABLE IF NOT EXISTS constraint_evaluation_results(
    constraint_name text,
    refinement_name text,
    rid integer,
    true_false text,
    FOREIGN KEY(rid) REFERENCES results(rid),
    FOREIGN KEY(constraint_name) REFERENCES Constraints(constraint_name),
    FOREIGN KEY(refinement_name) REFERENCES Refinements(refinement_name),
    CONSTRAINT pkey PRIMARY KEY (rid, constraint_name)
);

-- CREATE TABLE IF NOT EXISTS mappings(
--     rid integer,
--     slot_pos integer,
--     need_to_fetch_from_KG text,
--     value text,
--     CONSTRAINT pkey PRIMARY KEY (rid, slot_pos)
-- )

INSERT OR IGNORE INTO Refinements (refinement_name) VALUES
    ("ComparingGDP");

INSERT OR IGNORE INTO Constraints (constraint_name, refinement_name) VALUES
    ("SameUnitConstraint", "ComparingGDP"),
    ("MustBeSameKGAttrConstraint", "ComparingGDP"),
    ("ShouldDoPlottingConstraint", "ComparingGDP");