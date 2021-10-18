# BUILD
#docker build \
#--force-rm=true \
#-t squest \
#-f docker/squest.Dockerfile .

# RUN
#docker run -it --rm \
#-p 8000:8000 \
#squest

FROM python:3.8-slim-bullseye as python-base

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=Squest.settings
ENV POETRY_VERSION=1.1.5
ENV NODE_VERSION=12.22.6
ENV NVM_VERSION=v0.38.0
ENV NVM_DIR=/root/.nvm
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
ENV RUN_DEPS="git default-libmysqlclient-dev default-mysql-client graphviz curl libldap2-dev libsasl2-dev"
ENV BUID_DEPS="gcc"

# Install system deps
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends $RUN_DEPS $BUID_DEPS \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# STAGE BUILD
# ---------------------------
FROM python-base as builder

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install node and NPM
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/${NVM_VERSION}/install.sh | bash
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}

# Prepare a path to receive the project
RUN mkdir /app
WORKDIR /app
# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml package.json package-lock.json /app/

# Project libraries installation
RUN cd /app && poetry config virtualenvs.create false && poetry install && npm install

# Copy the full project
COPY . /app/
# Collect static files
RUN python manage.py collectstatic --noinput

# ---------------------------
# STAGE runtime
# ---------------------------
FROM python-base as runtime

# remove system build deps
RUN apt-get purge -y --auto-remove $BUID_DEPS

# Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.8.0/wait /wait
RUN chmod +x /wait

# Create media and backup folders
RUN mkdir -p /app/media /app/backup
COPY . /app/
COPY --from=builder /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/static /app/static

# Create a group and user to run our app
ARG APP_USER=django
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r --home /app -g ${APP_USER} ${APP_USER}
# Give rights to our user on all files
RUN chown -R ${APP_USER}:${APP_USER} /app
# Change to a non-root user
USER ${APP_USER}:${APP_USER}
WORKDIR /app
# Default entry point
CMD ["/app/docker/entrypoint.sh"]
