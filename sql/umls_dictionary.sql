DROP TABLE IF EXISTS "umls_dictionary" CASCADE;

CREATE TABLE "umls_dictionary"
(
    "umls_id" character varying(20) NOT NULL,
    "name" character varying NOT NULL,
    CONSTRAINT "umls_id_primary" PRIMARY KEY ("umls_id")
);