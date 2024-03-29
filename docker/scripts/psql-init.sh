#!/bin/bash
set -e

psql <<-EOSQL
    CREATE USER ${DB_USER} PASSWORD '${DB_PASSWORD}' NOSUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;
    CREATE DATABASE ${DB_DATABASE} OWNER ${DB_USER};
    GRANT ALL PRIVILEGES ON `test\_squest\_db` .  * TO '${DB_USER}'@'%';
EOSQL