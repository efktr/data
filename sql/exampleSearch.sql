SELECT drugbank_id, count("text")
	FROM public.search
    WHERE text ~* 'amphetamine'
GROUP BY drugbank_id;