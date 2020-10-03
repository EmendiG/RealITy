#!/bin/bash

# wait for Postgres to start and then start docker website service
function postgres_ready(){
python << END
import sys
import os
import psycopg2
try:
    conn = psycopg2.connect(dbname=os.environ.get('POSTGRES_DB'), user=os.environ.get('POSTGRES_USER'), password=os.environ.get('POSTGRES_PASSWORD'), host=os.environ.get('POSTGRES_HOST'))
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

python manage.py migrate

python manage.py runserver 0.0.0.0:8000