-- Find elements that start with "aspir"
SELECT reference, name, type , json_agg("text") AS synonyms, count("text") AS support
FROM search
WHERE text ~* '^aspir'
GROUP BY reference, name, type
ORDER BY support DESC;

-- Find elements that start with "headache"
SELECT reference, name, type , json_agg("text") AS synonyms, count("text") AS support
FROM search
WHERE text ~* '^headache'
GROUP BY reference, name, type
ORDER BY support DESC;

-- Find all drugs and products that give an ADR in > 50% of cases
SELECT drugbank.drugbank_id, drugbank.name, json_agg(joint_result.product) AS products
FROM drugbank
  JOIN (
         SELECT
           drugbank_products.product,
           drugbank_products.drugbank_id
         FROM drugbank_products,
           (
             SELECT DISTINCT (drugbank_id)
             FROM pubchem_to_drugbank,
               (
                 SELECT DISTINCT (adverse_drug_reactions.pubchem_id)
                 FROM adverse_drug_reactions,
                   (
                     SELECT DISTINCT (umls_id)
                     FROM umls_dictionary
                     WHERE umls_dictionary.name ~* '^headache'
                   ) AS interesting_adrs
                 WHERE adverse_drug_reactions.umls_id = interesting_adrs.umls_id AND
                       NUMRANGE(0.5, 1.0) @> adverse_drug_reactions.range
               ) AS interesting_ards_pubchem
             WHERE interesting_ards_pubchem.pubchem_id = pubchem_to_drugbank.pubchem_id
           ) AS interesting_db
         WHERE drugbank_products.drugbank_id = interesting_db.drugbank_id
       ) AS joint_result
    ON joint_result.drugbank_id = drugbank.drugbank_id
GROUP BY drugbank.drugbank_id;

-- High confidence ADRs --> can be considered trivial?
SELECT umls_dictionary.umls_id, umls_dictionary.name
FROM umls_dictionary
  JOIN (SELECT adrs.umls_id
        FROM adverse_drug_reactions as adrs
        WHERE NUMRANGE(0.9,1.0) @> adrs.range
        GROUP BY adrs.umls_id) AS high_adrs
    ON high_adrs.umls_id = umls_dictionary.umls_id;

-- Drugs that cause high confidence ADRs
SELECT dbjoin.name, json_agg(umlsdic.name)
FROM umls_dictionary AS umlsdic
  JOIN (
         SELECT
           db.name,
           mapped_ards.umls_id
         FROM drugbank AS db
           JOIN
           (SELECT
              ptd.drugbank_id,
              adr.umls_id
            FROM pubchem_to_drugbank AS ptd
              JOIN
              (SELECT *
               FROM adverse_drug_reactions
               WHERE NUMRANGE(0.9, 1.0) @> adverse_drug_reactions.range) AS adr
                ON adr.pubchem_id = ptd.pubchem_id) AS mapped_ards
             ON mapped_ards.drugbank_id = db.drugbank_id
       ) AS dbjoin
    ON dbjoin.umls_id = umlsdic.umls_id
GROUP BY dbjoin.name;

-- Select drug data based on drugbankId
SELECT
  db.drugbank_id,
  db.name,
  dbp.products,
  dbs.synonyms
FROM
  drugbank AS db,
  (
    SELECT drugbank_id, json_agg(product) AS products
    FROM drugbank_products
    WHERE drugbank_id = (
      SELECT drugbank_id
      FROM drugbank_id_mapping
      WHERE mapping = 'DB00001'
      LIMIT 1
    )
    GROUP BY drugbank_id
  ) AS dbp,
  (
    SELECT drugbank_id, json_agg(synonym) AS synonyms
    FROM drugbank_synonyms
    WHERE drugbank_id = (
      SELECT drugbank_id
      FROM drugbank_id_mapping
      WHERE mapping = 'DB00001'
      LIMIT 1
    )
    GROUP BY drugbank_id
  ) AS dbs
WHERE
  db.drugbank_id = (
    SELECT drugbank_id
    FROM drugbank_id_mapping
    WHERE mapping = 'DB00001'
    LIMIT 1
  ) AND
  db.drugbank_id = dbp.drugbank_id AND
  dbp.drugbank_id = dbs.drugbank_id;


-- Get ADRs for drug:

SELECT dict.umls_id, dict.name, adrs.lower, adrs.higher
FROM umls_dictionary as dict
  JOIN (
         SELECT DISTINCT
           umls_id,
           AVG(lower) as lower,
           AVG(higher) as higher
         FROM stitch_to_umls
         WHERE stitch_id = (
           SELECT stitch_id
           FROM stitch_to_drugbank
           WHERE drugbank_id = (
             SELECT drugbank_id
             FROM drugbank_id_mapping
             WHERE mapping = 'APRD00417'
             LIMIT 1
           )
           LIMIT 1) GROUP BY umls_id
       ) AS adrs
    ON adrs.umls_id = dict.umls_id;

-- Get drugs by ADR
SELECT db.drugbank_id, db.name
FROM drugbank AS db
  JOIN (
         SELECT drugbank_id
         FROM stitch_to_drugbank AS std
           JOIN (
                  SELECT DISTINCT stitch_id
                  FROM stitch_to_umls
                  WHERE umls_id = 'C0596240'
                ) AS stitch_mapping
             ON stitch_mapping.stitch_id = std.stitch_id
       ) AS drugbank_mapping
    ON drugbank_mapping.drugbank_id = db.drugbank_id;