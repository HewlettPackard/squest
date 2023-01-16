#!/usr/bin/env bash
ENV DATABASE=""

echo "Wait for required services to start"
/wait

echo "Applying database migration"
python manage.py migrate --database=${DATABASE:-default}

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Inserting default data"
python manage.py insert_default_data

echo "Starting web server"
gunicorn --bind 0.0.0.0:8000 --pythonpath /app/squest Squest.wsgi
