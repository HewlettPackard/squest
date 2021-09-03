# BUILD
#docker build \
#--force-rm=true \
#-t squest \
#-f docker/squest.Dockerfile .

# RUN
#docker run -it --rm \
#-p 8000:8000 \
#squest

FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=Squest.settings
ENV POETRY_VERSION=1.1.5

# Create a group and user to run our app
ARG APP_USER=django
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

# Install system deps
RUN set -ex \
    && RUN_DEPS=" \
    default-libmysqlclient-dev \
    gcc \
    curl \
    libldap2-dev libsasl2-dev \
    graphviz \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Install system deps
RUN pip install "poetry==$POETRY_VERSION"

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.8.0/wait /wait
RUN chmod +x /wait

# Install node and NPM
ENV NODE_VERSION=12.22.6
ENV NVM_VERSION=v0.38.0
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/${NVM_VERSION}/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

# Copy project code
RUN mkdir /app
WORKDIR /app
# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml package.json package-lock.json /app/

# Create a static and media folders
RUN mkdir /app/static && \
    mkdir /app/media && \
    mkdir /app/node_modules && \
    chown ${APP_USER}:${APP_USER} /app/static && \
    chown ${APP_USER}:${APP_USER} /app/media && \
    chown ${APP_USER}:${APP_USER} /app/node_modules

# Project initialization
RUN cd /app && poetry config virtualenvs.create false && poetry install
RUN cd /app && npm install

# Copy the full project
COPY . /app/

# Integrated web server port
EXPOSE 8000

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

# default entry point
CMD ["/app/docker/entrypoint.sh"]
