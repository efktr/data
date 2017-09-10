DROP VIEW IF EXISTS drugbank_id_mapping_lookup;


CREATE OR REPLACE VIEW drugbank_id_mapping_lookup AS
  SELECT drugbank_id, mapping
  FROM drugbank, unnest(other_ids) mapping
    UNION
  SELECT drugbank_id, drugbank_id as "mapping"
  FROM drugbank;