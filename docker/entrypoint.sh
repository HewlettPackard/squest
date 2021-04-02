#!/usr/bin/env bash

echo "Wait for required services to start"
/wait

echo "Applying database migration"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Inserting default data"
python manage.py insert_default_data

echo "Starting integrated web server"
python manage.py runserver 0.0.0.0:8000
