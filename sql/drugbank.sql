-- Table: public.drugbank

DROP TABLE IF EXISTS "drugbank" CASCADE;

CREATE TABLE "drugbank"
(
    "drugbank_id" character varying(20) NOT NULL,
    "name" character varying(255) NOT NULL,
    "other_ids" character varying(255)[],
    CONSTRAINT "drugbank_id_primary" PRIMARY KEY ("drugbank_id"),
    CONSTRAINT "name_unique" UNIQUE ("name")
);

DROP TABLE IF EXISTS "drugbank_products";

CREATE TABLE "drugbank_products"
(
    "drugbank_id" character varying(20) NOT NULL,
    "product" character varying NOT NULL,
    CONSTRAINT "product_pkey" PRIMARY KEY ("product"),
    CONSTRAINT "drugbank_fkey"  FOREIGN KEY ("drugbank_id")
        REFERENCES "drugbank" ("drugbank_id") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS "drugbank_synonyms";

CREATE TABLE "drugbank_synonyms"
(
    "drugbank_id" character varying(20) NOT NULL,
    "synonym" character varying NOT NULL,
    CONSTRAINT "synonym_pkey" PRIMARY KEY ("synonym"),
    CONSTRAINT "drugbank_fkey"  FOREIGN KEY ("drugbank_id")
        REFERENCES "drugbank" ("drugbank_id") MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);