#!/bin/bash
set -e

mysql --user=root --password=${DB_ROOT_PASSWORD} <<-EOSQL
    GRANT ALL PRIVILEGES ON test_squest_db.* TO '${DB_USER}'@'%';
EOSQL