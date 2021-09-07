#!/usr/bin/env bash

echo "Update certificate store"
update-ca-certificates

echo "Switch to django user"
su django

echo "Wait for required services to start"
/wait

echo "Applying database migration"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Inserting default data"
python manage.py insert_default_data

echo "Starting web server"
gunicorn --bind 0.0.0.0:8000 --pythonpath /app/squest Squest.wsgi
