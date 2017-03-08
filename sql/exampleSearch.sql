SELECT name, count("text") AS support
	FROM public.search
    WHERE text ~* '^aspir'
GROUP BY drugbank_id, name
ORDER BY support DESC;