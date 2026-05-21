FROM postgres:15-alpine

LABEL maintainer="Clínica Veterinária"
LABEL description="Banco de dados PostgreSQL para o sistema da clínica veterinária"

COPY init.sql /docker-entrypoint-initdb.d/init.sql

RUN chmod 644 /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
