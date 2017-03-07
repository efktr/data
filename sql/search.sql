DROP VIEW IF EXISTS search;

CREATE OR REPLACE VIEW search AS
  SELECT drugbank.drugbank_id,
    drugbank.name AS text,
    'drug' AS type
  FROM drugbank
  UNION ALL
  SELECT drugbank_synonyms.drugbank_id,
    drugbank_synonyms.synonym AS text,
    'drug' AS type
  FROM drugbank_synonyms
  UNION ALL
  SELECT drugbank_products.drugbank_id,
    drugbank_products.product AS text,
    'drug' AS type
  FROM drugbank_products;