-- Table: public.pubchem_to_drugbank

DROP TABLE IF EXISTS "stitch_to_drugbank";

CREATE TABLE "stitch_to_drugbank"
(
    "stitch_id" character varying(15) NOT NULL,
    "drugbank_id" character varying(300) NOT NULL,
    CONSTRAINT "stitch_to_drugbank_pkey"
    PRIMARY KEY ("stitch_id", "drugbank_id")
);