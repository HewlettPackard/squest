#!/bin/bash
set -e

psql --username "${POSTGRES_USER:-postgres}" --dbname "${POSTGRES_DB:-postgres}" \
    --set ON_ERROR_STOP=1 \
    --set db_user="${DB_USER:-squest_user}" \
    --set db_password="${DB_PASSWORD:-squest_password}" \
    --set db_database="${DB_DATABASE:-squest_db}" <<'EOSQL'
    CREATE USER :"db_user" PASSWORD :'db_password' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;
    CREATE DATABASE :"db_database" OWNER :"db_user";
EOSQL
