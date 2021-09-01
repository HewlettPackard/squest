# Configure settings

Settings are placed into the `squest/settings/development.py` file which is a standard [Django core settings file](https://docs.djangoproject.com/en/3.1/ref/settings/)

## LDAP backend

LDAP can be activated by setting the environment variable `LDAP_ENABLED` to `True` or directly in the `settings.py` file:

```python
LDAP_ENABLED= True
```

The configuration file need then to be created in `Squest/ldap_config.py`.

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
AUTH_LDAP_SERVER_URI = "ldaps://ad.example.com"
AUTH_LDAP_BIND_DN = "CN=my_app,OU=Service_Accounts,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', None)
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=Service_Accounts,DC=example,DC=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
LDAP_CA_FILE_PATH = "/path/to/my/company-ca.crt"
AUTH_LDAP_CONNECTION_OPTIONS: {
    ldap.OPT_X_TLS_CACERTFILE: LDAP_CA_FILE_PATH,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_ALLOW,
    ldap.OPT_X_TLS_NEWCTX: 0
}
AUTH_LDAP_START_TLS: True
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "uid"
}
```


## Email

Email settings are based on the [django settings](https://docs.djangoproject.com/en/3.1/ref/settings/#email-host)
```python
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = 25
```


## Time Zone

Set your time zone in `squest/settings/development.py`.

Default: 'Europe/Paris'

Value: A string representing the [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

```python
TIME_ZONE = 'Europe/Paris'
```
