#!/bin/bash
set -e

mariadb --user=root --password=${MYSQL_ROOT_PASSWORD} <<-EOSQL
    GRANT ALL PRIVILEGES ON test_squest_db.* TO '${MYSQL_USER}'@'%';
EOSQL
