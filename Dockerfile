# Dockerfile
# From  http://stackoverflow.com/questions/29600369/starting-and-populating-a-postgres-container-in-docker
FROM library/postgres

RUN apt-get update && apt-get -y install curl wget

WORKDIR /docker-entrypoint-initdb.d/
# From http://stackoverflow.com/a/29503623/5708679
RUN wget $(curl -s https://api.github.com/repos/efktr/data/releases/latest | grep 'browser_' | cut -d\" -f4)

EXPOSE 5432