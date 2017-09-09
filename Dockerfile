# Dockerfile
# From  http://stackoverflow.com/questions/29600369/starting-and-populating-a-postgres-container-in-docker
FROM library/postgres

RUN apt-get update && apt-get -y install curl wget


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

WORKDIR /docker-entrypoint-initdb.d/

# Create table definitions
RUN cat /usr/src/app/sql/drugbank.sql > /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/pubchem.sql >> /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/umls_dictionary.sql >> /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/adverse_drug_reactions.sql >> /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/pubchem_to_drugbank.sql >> /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/search.sql >> /docker-entrypoint-initdb.d/001structure.sql
RUN cat /usr/src/app/sql/stitch_to_drugbank.sql >> /docker-entrypoint-initdb.d/001structure.sql

# From http://stackoverflow.com/a/29503623/5708679
RUN wget -O 99data.sql $(curl -s https://api.github.com/repos/efktr/data/releases/latest | grep 'browser_' | cut -d\" -f4)

EXPOSE 5432