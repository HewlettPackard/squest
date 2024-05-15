# Setup a development environment

## Pre requisites

### Tools

Following tools need to be installed on your workstation:

- Docker
- Docker-compose
- Python 3.12
- Python virtualenv
- [Poetry](https://python-poetry.org/)
- npm

### System packages

Ubuntu based OS:
```bash
sudo apt-get install libmysqlclient-dev graphviz default-mysql-client libsqlite3-dev libsasl2-dev python3-dev libldap2-dev libssl-dev libpq-dev
```

CentOS/RedHat/Fedora
```bash
sudo yum install mysql-devel graphviz mysql libsq3-devel libpq-devel
```

## Start a development environment

The development environment is composed of 4 parts:

- **Docker compose:** The Docker compose file is used to deploy all required components such as the database and the message broker
- **Celery worker:** The Celery worker is a separated process that receive tasks from the main Django process to be executed asynchronously
- **Celery beat:** Celery beat is a periodic task scheduler that send task into the celery worker based on a frequency. This part is used by Squest to check the status of executed RHAAP/AWX job
- **Django built in web server:** Integrated web server used only for development purpose. main process of the application that serve the Web Ui and the API

### Docker compose

Run the Docker compose file with only required services to bring up database, message broker and other required system
```bash
docker-compose -f docker-compose.yml  -f dev.docker-compose.yml up db phpmyadmin rabbitmq redis-cache
```
If you use postgreSQL, update docker/environment_variables/squest.env, then run
```bash
docker-compose -f docker-compose.yml  -f psql.docker-composer.yml -f dev.docker-compose.yml up db phpmyadmin rabbitmq redis-cache
```

### Javascript libraries

Install JS libs (npm need to be installed)
```bash
npm install
```

### Python environment

Install python via pyenv then create a virtual environment for Squest
```
cd /path/to/squest
# install python
pyenv install 3.12.3
# create a venv
pyenv virtualenv 3.12.3 squest
# assign the venv to the current folder
pyenv local squest
# activate the env
pyenv activate squest
# Install poetry in the venv
pip3 install poetry
```

Initializing and installing python libraries with Poetry
```bash
poetry install
```

Go into the python virtual env
```bash
poetry shell
```

Create the database with Django migration script
```bash
python manage.py migrate
```

Collect static files
```bash
python manage.py collectstatic --noinput
```

Insert default data
```bash
python manage.py insert_default_data
```

### Celery worker and periodic task scheduler

Run Celery process for async tasks from a new terminal
```bash
poetry shell
celery -A service_catalog worker -l info
```

Run Celery beat for periodic tasks from a new terminal
```bash
poetry shell
celery -A service_catalog worker --beat -l info
```

### Django integrated web server

This next command should be executed from your IDE.

Run django dev server
```bash
poetry shell
python manage.py runserver
```

Settings are placed into the `squest/settings.py` file which is a standard [Django core settings file](https://docs.djangoproject.com/en/3.1/ref/settings/).

## Commands

To clean all Celery pending tasks
```bash
poetry shell
celery -A restapi purge
```

## Execute tests

Run unit tests
```bash
poetry shell
python manage.py test
```

Run code coverage
```bash
coverage run --source='.' manage.py test
# generate terminal report
coverage report
# generate HTML report
coverage html
```

## phpMyAdmin

phpMyAdmin is exposed on localhost:8082.

- server : db
- user : root
- password : p@ssw0rd
