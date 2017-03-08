DROP VIEW IF EXISTS search;

CREATE OR REPLACE VIEW search AS
  SELECT
    drugbank.drugbank_id,
    drugbank.name AS text,
    drugbank.name AS name,
    'drug' AS type
  FROM drugbank
  UNION ALL
  (
    SELECT
      db.drugbank_id,
      joint.text as text,
      db.name AS name,
      joint.type AS type
    FROM drugbank as db
      JOIN (SELECT
              drugbank_synonyms.drugbank_id,
              drugbank_synonyms.synonym AS text,
              'synonym' AS type
            FROM drugbank_synonyms
            UNION ALL
            SELECT
              drugbank_products.drugbank_id,
              drugbank_products.product AS text,
              'product' AS type
            FROM drugbank_products) AS joint ON db.drugbank_id = joint.drugbank_id
  );