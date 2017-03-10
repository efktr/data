# Dockerfile
#
# http://stackoverflow.com/questions/29600369/starting-and-populating-a-postgres-container-in-docker
FROM library/postgres


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

# Install pip
RUN apt-get update \
    && apt-get install -y python-pip

# Install python dependencies
RUN pip install -U pycurl
RUN pip install -U xmltodict
RUN pip install -U pubchempy

# Create table definitions
RUN cat sql/drugbank.sql >> /docker-entrypoint-initdb.d/$structure.sql \
    && cat sql/pubchem.sql >> /docker-entrypoint-initdb.d/$structure.sql \
    && cat sql/umls_dictionary.sql >> /docker-entrypoint-initdb.d/$structure.sql \
    && cat sql/adverse_drug_reactions.sql >> /docker-entrypoint-initdb.d/$structure.sql \
    && cat sql/pubchem_to_drugbank.sql >> /docker-entrypoint-initdb.d/$structure.sql \
    && cat sql/search.sql >> /docker-entrypoint-initdb.d/$structure.sql

COPY build.sh /docker-entrypoint-initdb.d/zBuild.sh

EXPOSE 5432
