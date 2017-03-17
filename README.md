# Data
Data sources, data collection scripts and database instantiation


## Release

1. Make sure the definitions in `\sql` match the ones on the db.
2. Export the DB data via `pg_dump -U postgres --data-only efktr > efktr.sql`
3. Attach efktr.sql to the release