# Setup a development environment

## Pre requisites

Pre-requisites:

- Docker
- Docker-compose
- Python 3.8
- Python virtualenv
- [Poetry](https://python-poetry.org/)

### System packages

Ubuntu based OS:
```
sudo apt-get install libmysqlclient-dev
```

CentOS/RedHat/Fedora
```
sudo yum install mysql-devel
```

### Python environment

Initialising and installing python libraries with Poetry
```
poetry init
```

## Start dev server

Run the Docker dev env to bring up database, message broker and other required system
```
docker-compose -f dev-env.docker-compose.yml up
```

Go into the python virtual env
```
poetry shell
```

Create the database with Django migration script
```
python manage.py migrate
```

Insert default data
```
python manage.py insert_default_data
```

Run django dev server
```
python manage.py runserver
```

Run Celery process for async tasks
```
celery -A restapi worker -l info
```

## Commands

To clean all Celery pending tasks
```
celery -A restapi purge
```