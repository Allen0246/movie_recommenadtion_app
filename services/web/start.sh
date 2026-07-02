#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

sleep 1

export FLASK_DEBUG=1
python3 -m flask run --cert=adhoc --no-reload --host=0.0.0.0
