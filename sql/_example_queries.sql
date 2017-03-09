-- Select drugs that contain words starting with "aspir" somewhere in their name, products or synonyms.
SELECT name, count("text") AS support
	FROM public.search
    WHERE text ~* '^aspir'
GROUP BY drugbank_id, name
ORDER BY support DESC;


-- High confidence ADRs
SELECT *
FROM adverse_drug_reactions
WHERE NUMRANGE(0.9,1.0) @> range;