#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo ".env не найден"
    exit 1
fi

export $(grep -v '^#' .env | xargs)

psql postgres <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_roles WHERE rolname = '$DB_USER'
   ) THEN
      CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
   END IF;
END
\$do\$;
EOF

psql postgres <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '$DB_NAME'
   ) THEN
      CREATE DATABASE $DB_NAME OWNER $DB_USER;
   END IF;
END
\$do\$;
EOF

PGPASSWORD=$DB_PASSWORD psql \
    -U $DB_USER \
    -d $DB_NAME \
    -f schema.sql

echo "БД успешно создана"
