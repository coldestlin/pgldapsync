################################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/ldaputils/users.py - LDAP user functions
#
# Copyright 2018, EnterpriseDB Corporation
#
################################################################################

import ldap
import sys


def get_ldap_users(config, conn, admin):
    """Get a list of users from the LDAP server.

    Args:
        config (ConfigParser): The application configuration
        conn (LDAPObject): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A list of user names
    """
    users = []

    scope_int = ldap.SCOPE_ONELEVEL
    scope_str = config.get('ldap', 'search_scope')
    if scope_str == 'SCOPE_BASE':
        scope_int = ldap.SCOPE_BASE
    elif scope_str == 'SCOPE_ONELEVEL':
        scope_int = ldap.SCOPE_ONELEVEL
    elif scope_str == 'SCOPE_SUBORDINATE':
        scope_int = ldap.SCOPE_SUBORDINATE
    elif scope_str == 'SCOPE_SUBTREE':
        scope_int = ldap.SCOPE_SUBTREE

    if admin:
        base_dn = config.get('ldap', 'admin_base_dn')
        search_filter = config.get('ldap', 'admin_filter_string')
    else:
        base_dn = config.get('ldap', 'base_dn')
        search_filter = config.get('ldap', 'filter_string')

    try:
        res = conn.search(base_dn, scope_int, search_filter)

        while 1:
            types, data = conn.result(res, 0)

            if not data:
                break

            record = data[0][1]

            users.append(record[config.get('ldap', 'username_attribute')][0])

    except ldap.LDAPError, e:
        if hasattr(e.message, 'info'):
            sys.stderr.write("Error retrieving LDAP users: [%s] %s\n" %
                            (e.message['desc'], e.message['info']))
        else:
            sys.stderr.write("Error retrieving LDAP users: %s\n" %
                            (e.message['desc']))
        return None

    return users


def get_filtered_ldap_users(config, conn, admin):
    """Get a filtered list of users from the LDAP server, having removed users
    to be ignored.

    Args:
        config (ConfigParser): The application configuration
        conn (LDAPObject): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A filtered list of user names
    """
    users = get_ldap_users(config, conn, admin)
    if users is None:
        return None

    # Remove ignored users
    for user in config.get('ldap', 'ignore_users').split(','):
        try:
            users.remove(user)
        except:
            pass

    return users
