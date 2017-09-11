-- Table: public.pubchem_to_drugbank

DROP TABLE IF EXISTS "stitch_to_umls";

CREATE TABLE "stitch_to_umls"
(
    "stitch_id" character varying(15) NOT NULL,
    "umls_id" character varying(300) NOT NULL,
    "lower" double precision,
    "higher" double precision,
    CONSTRAINT "stitch_to_umls_pkey"
    PRIMARY KEY ("stitch_id", "umls_id")
);