# LDAP authentication backend

## Default configuration

The configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

### LDAP_ENABLED

**Default:** `False`

Set to `True` to enable LDAP based authentication.  


### AUTH_LDAP_SERVER_URI

**Default:** `ldap:port`

Set the LDAP serveur URI and port

### AUTH_LDAP_BIND_DN

**Default:** `cn=service_account_name,ou=Applications,o=domain.com`

Set the LDAP DN to authenticate to the LDAP serveur

### AUTH_LDAP_BIND_PASSWORD

**Default:** `NONE`

Associated to AUTH_LDAP_BIND_DN, password used to authenticate DN

### AUTH_LDAP_USER_SEARCH

**Default:** `ou=People,o=domain.com`

User search patern

### AUTH_LDAP_ATTR_FIRSTNAME

**Default:** `givenName`

set the LDAP "first_name" attribute

### AUTH_LDAP_ATTR_LASTNAME

**Default:** `sn`

set the LDAP "last_name" attribute

### AUTH_LDAP_ATTR_MAIL

**Default:** `mail`

set the LDAP "email" attribute


## Advanced configuration

LDAP can be activated by setting the environment variable `LDAP_ENABLED` to `True` in your configuration:
```bash
LDAP_ENABLED=True
```

You can overide the given configuration by using the `ldap.docker-compose.yml` file and mount your custom `ldap_config.py`.
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
