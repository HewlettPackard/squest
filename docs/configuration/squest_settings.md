# Configuration  settings

Default settings are configured to provide a testing/development environment. For a production setup it is recommended
to adjust them following your target environment.

When using docker-compose, the configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

When using Kubernetes, the configuration need to be placed in the `squest.yml` inventory file in the variable `squest_django/env`.

## Database

### DATABASE

**Default:** `default`

Setup mysql database usage
Set to `psql` for postgres SQL usage

### DB_DATABASE

**Default:** `squest_db`

Database name.

### DB_USER

**Default:** `squest_user`

User used to connect to the `DB_DATABASE` name.

### DB_PASSWORD

**Default:** `squest_password`

Password of the `DB_USER` username.

### DB_HOST

**Default:** `127.0.0.1`

Database host. The default value is localhost to match the development configuration.
Switch to `db` in production when using the docker-compose based deployment.

### DB_PORT

**Default:** `3306`

Database port.

## Authentication

### LDAP

#### LDAP_ENABLED

**Default:** `False`

Set to `True` to enable LDAP based authentication.

#### AUTH_LDAP_SERVER_URI

**Default:** `NONE`

Set the URI of your LDAP server, using a protocol prefix (`ldap://` or `ldaps://`) and the server's hostname, e.g. `ldaps://ldap.example.com`.

#### AUTH_LDAP_BIND_DN

**Default:** `NONE`

Set the LDAP DN to authenticate to the LDAP server, e.g. `cn=service_account_name,ou=Applications,o=domain.com`.

#### AUTH_LDAP_BIND_PASSWORD

**Default:** `NONE`

Associated to AUTH_LDAP_BIND_DN, this sets the password used to authenticate

#### AUTH_LDAP_USER_SEARCH

**Default:** `NONE`

Base DN for the user search, e.g. `ou=People,o=domain.com`

#### AUTH_LDAP_USER_SEARCH_FILTER

**Default:** `(uid=%(user)s)`

LDAP search filter for the user search. For connections to an Active Directory this is normally set to `(sAMAccountName=%(user)s)`.

#### AUTH_LDAP_ATTR_FIRSTNAME

**Default:** `givenName`

set the LDAP "first_name" attribute

#### AUTH_LDAP_ATTR_LASTNAME

**Default:** `sn`

set the LDAP "last_name" attribute

#### AUTH_LDAP_ATTR_MAIL

**Default:** `mail`

set the LDAP "email" attribute

### Social Authentication

Squest supports external authentication providers (GitHub Enterprise, OpenID Connect, Google, etc.) through the [python-social-auth](https://python-social-auth.readthedocs.io/) library.

#### SOCIAL_AUTH_OIDC_ENABLED

**Default:** `False`

Set to `True` to enable social authentication. When enabled, Squest loads a dedicated configuration file `Squest/social_auth_config.py` at the end of the main settings.

#### Configuring a social auth provider

All social authentication settings are defined in the file `Squest/social_auth_config.py`. This file is only loaded when `SOCIAL_AUTH_OIDC_ENABLED` is `True`.

It contains:

- **`SOCIAL_AUTH_OIDC_BTN_TEXT`** - The text displayed on the login button. Default: `"Github enterprise"`.
- **`SOCIAL_AUTH_SELECTED_BACKEND`** - The backend slug used to build the login URL (e.g. `github-enterprise`, `oidc`, `google-oauth2`). Must match the `name` attribute of the selected `python-social-auth` backend.
- **Provider-specific settings** - Keys, secrets, URLs, and scopes required by the chosen provider (e.g. `SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY`, `SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET`, `SOCIAL_AUTH_OIDC_KEY`, `SOCIAL_AUTH_OIDC_SECRET`).
- **`SOCIAL_AUTH_PIPELINE`** - The ordered list of pipeline steps executed during authentication. A custom step can be added to customize user creation (e.g. mapping the OAuth email to the Django username).
- **`AUTHENTICATION_BACKENDS`** - The list of Django authentication backends. The selected `python-social-auth` backend must be listed here.

To switch to a different provider (e.g. from GitHub Enterprise to OpenID Connect), edit `Squest/social_auth_config.py`:

1. Update `SOCIAL_AUTH_SELECTED_BACKEND` to match the new backend slug (e.g. `oidc`).
2. Uncomment/add the provider-specific settings (endpoint, key, secret).
3. Update `AUTHENTICATION_BACKENDS` to use the corresponding backend class.

Refer to the [python-social-auth documentation](https://python-social-auth.readthedocs.io/en/latest/backends/index.html) for the full list of supported backends and their required settings.

### Password & token

#### PASSWORD_ENABLED

**Default:** `True`

set to `False` to disable the password form on the login view

#### DEFAULT_ADMIN_PASSWORD

**Default:** `None`

Set a default password to the admin user when starting Squest.

#### LOGIN_HELPER_TEXT

**Default:** `None`

Add a custom note into the login page that helps user to know what are the expected credentials. HTML text is supported.

E.G: "Use your corporate email and password".

#### DEFAULT_ADMIN_TOKEN

**Default:** `None`

Set an API token that will be linked to the admin user when starting Squest.


## Squest

### MAINTENANCE_MODE_ENABLED

**Default:** `False`

When enabled, only administrators can access squest UI and API.
This can be used for example to block new requests by end users from the service catalog. So an administrator can perform operations against the API like migrating instance specs.

!!! note

    This can also be set on the fly from the admin panel (top right corner of the UI) in the object `Squest settings`.

### SQUEST_HOST

**Default:** `http://squest.domain.local`

Address of the Squest portal instance. Used in email templates and in metadata sent to Red Hat Ansible Automation Platform/AWX job templates.

### SQUEST_ADMINS

**Default:** `''`

Comma separated list of email who get code error notifications. When DEBUG=False.
Example:

```text
elias.boulharts@mail.com,nicolas.marcq@mail.com
```

### IS_DEV_SERVER

**Default:** `False`

Set to `True` to change the navbar and footer color to visually identify a testing instance of Squest.

### GUNICORN_WORKERS

**Default:** `4`

Number of workers used by Gunicorn process in charge of serving client connection. Increase the number of worker threads to serve more clients concurrently

### DOC_IMAGES_CLEANUP_ENABLED

**Default:** `False`

Switch to `True` to enable automatic cleanup of ghost docs images from media folder.

### DOC_IMAGES_CLEANUP_CRONTAB

**Default:** `30 1 * * *`

Crontab line for ghost image cleanup. By default performed every day at 1:30 AM.

## SMTP

### SQUEST_EMAIL_NOTIFICATION_ENABLED

**Default:** Based on `DEBUG` value by default

Set to `True` to enable email notifications.  

### SQUEST_EMAIL_HOST

**Default:** `squest@squest.domain.local`

Domain name used as email sender. E.g: "squest@squest.domain.local". 

### EMAIL_HOST

**Default:** `localhost`

The SMTP host to use for sending email.

### EMAIL_PORT

**Default:** `25`

Port to use for the SMTP server defined in `EMAIL_HOST`.

### EMAIL_HOST_USER

**Default:** `None`

User to use to authenticate with the SMTP server defined in `EMAIL_HOST` in combination with `EMAIL_HOST_PASSWORD`. Leave empty/unconfigured to send emails unauthenticated.

### EMAIL_HOST_PASSWORD

**Default:** `None`

Password to use to authenticate with the SMTP server defined in `EMAIL_HOST` in combination with `EMAIL_HOST_USER`. Leave empty/unconfigured to send emails unauthenticated.

### EMAIL_USE_SSL

**Default:** `False`

Whether to use an implicit TLS (secure) connection when talking to the SMTP server defined in `EMAIL_HOST`.

## Backup

### BACKUP_ENABLED

**Default:** `False`

Switch to `True` to enable backup. Refer to the [dedicated documentation](../administration/backup.md).

### BACKUP_CRONTAB

**Default:** `0 1 * * *`

Crontab line for backup. By default, the backup is performed every day at 1AM.

### DBBACKUP_CLEANUP_KEEP

**Default:** `5`

Number of db backup file to keep. [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media).

### DBBACKUP_CLEANUP_KEEP_MEDIA

**Default:** `5`

Number of media backup tar to keep. [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media).

## Metrics

### METRICS_ENABLED

**Default:** `False`

Switch to `True` to enable Prometheus metrics page.

### METRICS_PASSWORD_PROTECTED

**Default:** `True`

Switch to `False` to disable the basic authentication on metrics page.

### METRICS_AUTHORIZATION_USERNAME

**Default:** `admin`

Username for the basic authentication of the metrics page.

### METRICS_AUTHORIZATION_PASSWORD

**Default:** `admin`

Password for the basic authentication of the metrics page.

## Django

### SECRET_KEY

**Default:**  Default randomly-generated

Django secret key used for cryptographic signing. [Doc](https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-SECRET_KEY).

### DEBUG

**Default:** `True`

Django DEBUG mode. Switch to `False` for production.

### SQL_DEBUG

**Default:** `False`

Enables SQL debug logs.

### ALLOWED_HOSTS

**Default:** `*`

Comma separated list of allowed FQDN. Refer to the complete [documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts).

### CSRF_TRUSTED_ORIGINS

**Default:** `http://127.0.0.1:8080,http://localhost:8080`

Comma separated list of trusted origin.
Refer to the complete [documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins).

!!! note

    If you deploy with `http://1.2.3.4:8080`, please add `CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8080,http://localhost:8080,http://1.2.3.4:8080` in your variables.

### LANGUAGE_CODE

**Default:** `en-us`

Django language. [Doc](https://docs.djangoproject.com/en/4.2/ref/settings/#language-code)

### TIME_ZONE

**Default:** `Europe/Paris`

Time zone of the server that host Squest service. [Doc](https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-TIME_ZONE)

### DATE_FORMAT

**Default:** `%d %b, %Y  %H:%M`

Change the format of all date in Squest UI. Based on Python [strftime](https://strftime.org/).

## RabbitMQ

RabbitMQ is used as message broker for asynchronous tasks executed by Squest via the "[Celery](https://docs.celeryq.dev/)" python library.

### RABBITMQ_USER

**Default:** rabbitmq

RabbitMQ message broker user.

### RABBITMQ_PASSWORD

**Default:** rabbitmq

RabbitMQ message broker password.

### RABBITMQ_HOST

**Default:** localhost

RabbitMQ message broker host. The default value is `localhost` to match the development configuration. 
Replace `localhost` by `rabbitmq` in production when using the docker-compose or kubernetes based deployment.

### RABBITMQ_PORT

**Default:** 5672

RabbitMQ message broker port.

### RABBITMQ_VHOST

**Default:** squest

RabbitMQ message broker vhost.

## Redis

### REDIS_CACHE_USER

**Default:** `default`

Username of Redis account.

### REDIS_CACHE_PASSWORD

**Default:** `redis_secret_password`

Password of Redis account.

### REDIS_CACHE_HOST

**Default:** `127.0.0.1`

Redis hostname.

### REDIS_CACHE_PORT

**Default:** `6379`

Redis port.
