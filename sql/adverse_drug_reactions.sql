DROP TABLE IF EXISTS "adverse_drug_reactions" CASCADE;

CREATE TABLE "adverse_drug_reactions"
(
  "pubchem_id" INT NOT NULL,
  "umls_id" character varying(15) NOT NULL,
  "range" numrange NOT NULL,
  "support" INT NOT NULL,

  CONSTRAINT "ard_primary" PRIMARY KEY ("pubchem_id", "umls_id"),
  CONSTRAINT "pubchem_fkey"  FOREIGN KEY ("pubchem_id")
  REFERENCES "pubchem" ("pubchem_id") MATCH SIMPLE
  ON UPDATE CASCADE
  ON DELETE CASCADE,

  CONSTRAINT "umls_fkey"  FOREIGN KEY ("umls_id")
  REFERENCES "umls_dictionary" ("umls_id") MATCH SIMPLE
  ON UPDATE CASCADE
  ON DELETE CASCADE
);