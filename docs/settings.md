# Configure settings

## LDAP backend

LDAP can be activated by setting the environment vairable `LDAP_ENABLED` to `True` or directly in the settings.py file:

```python
LDAP_ENABLED= True
```

The configuration file need then to be created in `TowerServiceCatalog/ldap_config.py`.

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
