# Configure settings

Default settings are configured to provide a testing/development environment. For a production setup it is recommended
to adjust them following you production target environment.

The configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

## Environment variables

| Variable                          | Default                                          | Comment                                                                                                                              |
| --------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| SECRET_KEY                        | Default randomly-generated                       | Django secret key used for cryptographic signing. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-SECRET_KEY). |
| DEBUG                             | `TRUE`                                           | Django DEBUG mode.                                                                                                                   |
| ALLOWED_HOSTS                     | `*`                                              | Comma separated list of allowed FQDN. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts).                      |
| MYSQL_DATABASE                    | `squest_db`                                      | Mysql database name.                                                                                                                 |
| MYSQL_USER                        | `squest_user`                                    | Mysql user used to connect to the DB name.                                                                                           |
| MYSQL_PASSWORD                    | `squest_password`                                | Password of the mysql user name.                                                                                                     |
| MYSQL_HOST                        | `127.0.0.1`                                      | Mysql DB host. Switch to `db` when not in dev env.                                                                                   |
| MYSQL_PORT                        | `3306`                                           | Mysql DB port.                                                                                                                       |
| LDAP_ENABLED                      | `False`                                          | Set to `True` to enable LDAP based authentication. See configuration below.                                                          |
| CELERY_BROKER_URL                 | `amqp://rabbitmq:rabbitmq@localhost:5672/squest` | Rabbitmq URL. Replace `localhost` by `rabbitmq` when not in dev env.                                                                 |
| CELERYD_TASK_SOFT_TIME_LIMIT      | `300`                                            | Async task execution timeout. [Doc](https://docs.celeryproject.org/en/v2.2.4/configuration.html#celeryd-task-soft-time-limit).       |
| SQUEST_HOST                       | `squest.domain.local`                            | Domain name used as email sender. E.g: "squest@squest.domain.local".                                                                 |
| SQUEST_EMAIL_NOTIFICATION_ENABLED | Based on `DEBUG` value by default                | Set to `True` to enable email notification.                                                                                          |
| EMAIL_HOST                        | `localhost`                                      | The SMTP host to use for sending email.                                                                                              |
| EMAIL_PORT                        | `25`                                             | Port to use for the SMTP server defined in `EMAIL_HOST`.                                                                             |
| LANGUAGE_CODE                     | `en-us`                                          | Django language. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#language-code)                                            |
| TIME_ZONE                         | `Europe/Paris`                                   | Time zone of the server that host Squest service. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-TIME_ZONE)   |

## LDAP backend

LDAP can be activated by setting the environment variable `LDAP_ENABLED` to `True` in your configuration:
```bash
LDAP_ENABLED=True
```

The configuration is based on the Django plugin `django-auth-ldap`.
You can follow the [official documentation](https://django-auth-ldap.readthedocs.io/en/latest/authentication.html#)
to know available configuration options.

Example of `ldap_config.py`:

```python
import os
import ldap
from django_auth_ldap.config import LDAPSearch

print("LDAP config loaded")
# -----------------------
# LDAP auth backend
# -----------------------
AUTH_LDAP_SERVER_URI = "ldaps://ad.example.com:636"
AUTH_LDAP_BIND_DN = "CN=my_app,OU=Service_Accounts,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', None)
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=Service_Accounts,DC=example,DC=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
LDAP_CA_FILE_PATH = "/usr/local/share/ca-certificates/ldap_ca.crt"  # default path in ldap docker compose file
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_X_TLS_CACERTFILE: LDAP_CA_FILE_PATH,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_ALLOW,
    ldap.OPT_X_TLS_NEWCTX: 0
}
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "uid"
}
```

Update the `ldap.docker-compose.yml` file to mount your configuration file and the CA certificate of the LDAP 
server (if LDAPS is used) in django and celery containers:
```yaml
  django:
    volumes:
      - ./Squest/ldap_config.py:/app/Squest/ldap_config.py
      - ./docker/certs/ldap_ca.crt:/usr/local/share/ca-certificates/ldap_ca.crt
  celery-worker:
    volumes:
      - ./Squest/ldap_config.py:/app/Squest/ldap_config.py
      - ./docker/certs/ldap_ca.crt:/usr/local/share/ca-certificates/ldap_ca.crt
  celery-beat:
    volumes:
      - ./Squest/ldap_config.py:/app/Squest/ldap_config.py
      - ./docker/certs/ldap_ca.crt:/usr/local/share/ca-certificates/ldap_ca.crt
```

Run docker compose with the ldap config
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml -f ldap.docker-compose.yml up 
```
