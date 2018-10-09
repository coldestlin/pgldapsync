import ldap
import os
import sys

##########################################################################
# LDAP access configuration
##########################################################################

# LDAP server connection details
LDAP_SERVER_URI = "ldap://ldap.example.com"

# The base DN for the search
LDAP_BASE_DN = "ou=People,dc=example,dc=com"

# User to bind to the directory as. Leave empty for anonymous binding.
LDAP_BIND_USERNAME = ""
LDAP_BIND_PASSWORD = ""

# Search scope for users
LDAP_SEARCH_SCOPE = ldap.SCOPE_SUBTREE

# The LDAP attribute containing user names. In OpenLDAP, this may be 'uid'
# whilst in AD, 'sAMAccountName' might be appropriate.
LDAP_USERNAME_ATTRIBUTE = 'uid'

# An array of users to ignore
LDAP_IGNORE_USERS = ['Manager']


##########################################################################
# Postgres access configuration
##########################################################################

# Postgres server connection string
PG_SERVER_CONNSTR = "hostaddr=127.0.0.1 port=5432 user=postgres dbname=postgres"

# An array of login role names to ignore
PG_IGNORE_LOGIN_ROLES = ['postgres']

##########################################################################
# General configuration
##########################################################################

# Add LDAP users to Postgres if they don't exist, or ignore them?
ADD_LDAP_USERS_TO_POSTGRES = True

# Remove Postgres login roles if they don't exist in LDAP, or ignore them?
REMOVE_LOGIN_ROLES_FROM_POSTGRES = True

##########################################################################
# Load local config overrides
##########################################################################

try:
    from config_local import *
except ImportError:
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "config_local.py")
    msg = "The local configuration file (%s) could not " \
          "be found.\nPlease create the file and try again.\n" % path

    sys.stderr.write(msg)
    sys.exit(1)
