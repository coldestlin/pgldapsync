################################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# pgldapsync/pgutils/roles.py - Postgres role functions
#
# Copyright 2018, EnterpriseDB Corporation
#
################################################################################

import psycopg2
import sys


def get_pg_login_roles(conn):
    """Get a list of login roles from the Postgres server.

    Args:
        conn (connection): The Postgres connection object
    Returns:
        str[]: A list of user names
    """
    cur = conn.cursor()

    try:
        cur.execute("SELECT rolname FROM pg_authid WHERE rolcanlogin;")
        rows = cur.fetchall()
    except psycopg2.Error, e:
        sys.stderr.write("Error retrieving Postgres login roles: %s\n" % e)
        return None

    roles = []

    for row in rows:
        roles.append(row[0])

    cur.close()

    return roles


def get_filtered_pg_login_roles(config, conn):
    """Get a filtered list of login roles from the Postgres server, having
    removed users to be ignored.

    Args:
        config (ConfigParser): The application configuration
        conn (connection): The Postgres connection object
    Returns:
        str[]: A filtered list of login roles
    """
    roles = get_pg_login_roles(conn)
    if roles is None:
        return None

    # Remove ignored roles
    for role in config.get('postgres', 'ignore_login_roles').split(','):
        try:
            roles.remove(role)
        except:
            pass

    return roles


def get_role_attributes(config):
    """Generate a list of role attributes to use when creating login roles

    Args:
        config (ConfigParser): The application configuration
    Returns:
        str: A SQL snippet listing the role attributes
    """
    attribute_list = ''
    if config.getboolean('general', 'role_attribute_superuser'):
        attribute_list = attribute_list + 'SUPERUSER'
    else:
        attribute_list = attribute_list + 'NOSUPERUSER'

    if config.getboolean('general', 'role_attribute_createdb'):
        attribute_list = attribute_list + ' CREATEDB'
    else:
        attribute_list = attribute_list + ' NOCREATEDB'

    if config.getboolean('general', 'role_attribute_createrole'):
        attribute_list = attribute_list + ' CREATEROLE'
    else:
        attribute_list = attribute_list + ' NOCREATEROLE'

    if config.getboolean('general', 'role_attribute_noinherit'):
        attribute_list = attribute_list + ' NOINHERIT'
    else:
        attribute_list = attribute_list + ' INHERIT'

    if config.getboolean('general', 'role_attribute_bypassrls'):
        attribute_list = attribute_list + ' BYPASSRLS'
    else:
        attribute_list = attribute_list + ' NOBYPASSRLS'

    if config.getint('general', 'role_attribute_connection_limit') != -1:
        attribute_list = attribute_list + ' CONNECTION LIMIT ' + \
                         str(config.getint('general',
                                               'role_attribute_connection_limit'
                                               ))

    return attribute_list


def get_role_grants(config, role, with_admin=False):
    """Get a SQL string to GRANT membership to the configured roles when
    creating a new login role.

    Args:
        config (ConfigParser): The application configuration
        role (str): The role name to be granted additional roles
        with_admin (bool): Generate a list of roles that will have the WITH
            ADMIN OPTION specified, if True
    Returns:
        str: A SQL snippet listing the role GRANT statements required
    """
    roles = ''
    sql = ''

    if with_admin:
        roles_to_grant = config.get('general',
                                    'roles_to_grant_with_admin').split(',')
    else:
        roles_to_grant = config.get('general', 'roles_to_grant').split(',')

    for r in roles_to_grant:
        roles = roles + '"' + r + '", '

    if roles.endswith(', '):
        roles = roles[:-2]

    if roles != '':
        sql = 'GRANT %s TO "%s"' % (roles, role)

        if with_admin:
            sql = sql + " WITH ADMIN OPTION"

        sql = sql + ';'

    return sql