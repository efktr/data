DROP TABLE IF EXISTS "pubchem" CASCADE;

CREATE TABLE "pubchem"
(
  "pubchem_id" INT NOT NULL,
  "stitch_id" character varying(15) NOT NULL,
  "stitch_id_flat" character varying(15) NOT NULL,
  CONSTRAINT "pubchem_id_primary" PRIMARY KEY ("pubchem_id")
);