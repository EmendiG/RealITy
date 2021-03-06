#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE realestate_zero;
    GRANT ALL PRIVILEGES ON DATABASE "$DATABASE_NAME" TO "$POSTGRES_USER";
EOSQL