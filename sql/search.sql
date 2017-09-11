-- View: public.search

DROP VIEW IF EXISTS search;

CREATE OR REPLACE VIEW search AS
  SELECT
    umlsdict.umls_id as reference,
    umlsdict.name AS text,
    umlsdict.name AS name,
    'adr' AS type
  FROM umls_dictionary AS umlsdict
  UNION
  (
    SELECT
      drugbank.drugbank_id as reference,
      drugbank.name AS text,
      drugbank.name AS name,
      'drug' AS type
    FROM drugbank
    UNION
    (
      SELECT
        db.drugbank_id AS reference,
        joint.text AS TEXT,
        db.name AS NAME,
        joint.type AS TYPE
      FROM drugbank AS db
        JOIN ( SELECT
                 drugbank_synonyms.drugbank_id AS reference,
                 drugbank_synonyms.synonym AS TEXT,
                 'synonym' AS TYPE
               FROM drugbank_synonyms
               UNION
               SELECT
                 drugbank_products.drugbank_id AS reference,
                 drugbank_products.product AS TEXT,
                 'product' AS TYPE
               FROM drugbank_products) AS joint
          ON db.drugbank_id = joint.reference
    )
  );