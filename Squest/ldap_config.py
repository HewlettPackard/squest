import os
import ldap
from django_auth_ldap.config import LDAPSearch

print("LDAP config loaded")
# -----------------------
# LDAP auth backend
# -----------------------
AUTH_LDAP_SERVER_URI = os.environ.get('AUTH_LDAP_SERVER_URI', None)
AUTH_LDAP_BIND_DN = os.environ.get('AUTH_LDAP_BIND_DN', None)
AUTH_LDAP_BIND_PASSWORD = os.environ.get('AUTH_LDAP_BIND_PASSWORD', None)
AUTH_LDAP_USER_SEARCH = LDAPSearch(os.environ.get('AUTH_LDAP_USER_SEARCH', None), ldap.SCOPE_SUBTREE, os.environ.get('AUTH_LDAP_USER_SEARCH_FILTER', "(uid=%(user)s)"))
LDAP_CA_FILE_PATH = os.environ.get('LDAP_CA_FILE_PATH', "/etc/ssl/certs/ca-certificates.crt")

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_X_TLS_CACERTFILE: LDAP_CA_FILE_PATH,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_ALLOW,
    ldap.OPT_X_TLS_NEWCTX: 0
}

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": os.environ.get('AUTH_LDAP_ATTR_FIRSTNAME', 'givenName'),
    "last_name": os.environ.get('AUTH_LDAP_ATTR_LASTNAME', 'sn'),
    "email": os.environ.get('AUTH_LDAP_ATTR_MAIL', 'mail')
}
