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

## Start a development environment

The development environment is composed of 4 parts:

- **Docker compose:** The Docker compose file is used to deploy all required components such as the database and the message broker
- **Celery worker:** The Celery worker is a separated process that receive tasks from the main Django process to be executed asynchronously 
- **Celery beat:** Celery beat is a periodic task scheduler that send task into the celery worker based on a frequency. This part is used by Squest to check the status of executed Tower job
- **Django built in web server:** Integrated web server used only for development purpose. main process of the application that serve the Web Ui and the API

### Docker compose

Run the Docker dev env to bring up database, message broker and other required system
```
docker-compose -f dev-env.docker-compose.yml up
```

### Celery worker and periodic task scheduler

Run Celery process for async tasks
```
poetry shell
celery -A service_catalog worker -l info
```

Run Celery beat for periodic tasks
```
poetry shell
celery -A service_catalog worker --beat --scheduler django -l info
```

### Django integrated web server

Run django dev server
```
poetry shell
python manage.py runserver
```

## Commands

To clean all Celery pending tasks
```
poetry shell
celery -A restapi purge
```
