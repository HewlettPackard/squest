import os
import ldap
from django_auth_ldap.config import LDAPSearch

print("LDAP config loaded")
# -----------------------
# LDAP auth backend
# -----------------------
AUTH_LDAP_SERVER_URI = "ldap:port"
AUTH_LDAP_BIND_DN = "cn=service_account_name,ou=Applications,o=domain.com"
AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', None)
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=People,o=domain.com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
LDAP_CA_FILE_PATH = "/usr/local/share/ca-certificates/ldap_ca.crt"
AUTH_LDAP_CONNECTION_OPTIONS: {
    ldap.OPT_X_TLS_CACERTFILE: LDAP_CA_FILE_PATH,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
    ldap.OPT_X_TLS_NEWCTX: 0
}
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "uid"
}
