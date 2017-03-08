-- Table: public.pubchem_to_drugbank

DROP TABLE IF EXISTS "pubchem_to_drugbank";

CREATE TABLE "pubchem_to_drugbank"
(
    "pubchem_id" int NOT NULL,
    "drugbank_id" character varying(300) NOT NULL,
    CONSTRAINT "pubchem_to_drugbank_pkey"  PRIMARY KEY ("pubchem_id", "drugbank_id"),
    CONSTRAINT "drugbank_fkey"  FOREIGN KEY ("drugbank_id")
    REFERENCES "drugbank" ("drugbank_id") MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    CONSTRAINT "pubchem_fkey"  FOREIGN KEY ("pubchem_id")
    REFERENCES "pubchem" ("pubchem_id") MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE
);