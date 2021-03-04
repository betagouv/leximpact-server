#!/bin/bash
cd /opt/leximpact-server
set -e
sleep 1
echo "$DATABASE_USER@$DATABASE_HOST:$DATABASE_PORT"
until PGPASSWORD=$DATABASE_PASS psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up !"

echo "leximpact-server : make migrate..."
make migrate
echo "leximpact-server : make run..."
make run