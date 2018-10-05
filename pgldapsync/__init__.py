import argparse
import sys

from pgldapsync.ldaputils.connection import connect_ldap_server
from pgldapsync.ldaputils.users import *
from pgldapsync.pgutils.connection import connect_pg_server
from pgldapsync.pgutils.roles import *


def get_create_login_roles(ldap_users, pg_roles):
    roles = []

    for user in ldap_users:
        if user not in pg_roles:
            roles.append(user)

    return roles


def get_drop_login_roles(ldap_users, pg_roles):
    roles = []

    for role in pg_roles:
        if role not in ldap_users:
            roles.append(role)

    return roles


def main():
    """
    The core structure of the app
    """

    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Synchronise users and groups from LDAP/AD to PostgreSQL.')
    parser.add_argument("--dry-run", "-d", action='store_true',
                        help="don't apply changes to the database server, "
                             "dump the SQL to stdout instead")

    args = parser.parse_args()

    if args.dry_run:
        print("-- This is an LDAP sync dry run.")
        print("-- The commands below can be manually executed if required.")

    # Get the LDAP users
    ldap_conn = connect_ldap_server(config.LDAP_SERVER_URI)
    if ldap_conn is None:
        sys.exit(1)

    ldap_users = get_filtered_ldap_users(ldap_conn)
    if ldap_users is None:
        sys.exit(1)

    # Get the Postgres users
    pg_conn = connect_pg_server(config.PG_SERVER_CONNSTR)
    if pg_conn is None:
        sys.exit(1)

    pg_login_roles = get_filtered_pg_login_roles(pg_conn)
    if pg_login_roles is None:
        sys.exit(1)


    login_roles_to_create = get_create_login_roles(ldap_users, pg_login_roles)
    login_roles_to_drop = get_drop_login_roles(ldap_users, pg_login_roles)

    # Create/drop roles if required
    have_work = ((config.ADD_LDAP_USERS_TO_POSTGRES and
                  len(login_roles_to_create) > 0) or
                    (config.REMOVE_LOGIN_ROLES_FROM_POSTGRES and
                     len(login_roles_to_drop) > 0))

    roles_added = 0
    roles_dropped = 0

    if have_work:
        if args.dry_run:
            print("BEGIN;")
        else:
            cur = pg_conn.cursor()
            cur.execute("BEGIN;")

    if config.ADD_LDAP_USERS_TO_POSTGRES:
        for role in login_roles_to_create:
            if args.dry_run:
                print("""CREATE ROLE "%s" LOGIN;""" % role.replace('\'', '\\\''))
            else:
                cur.execute("""CREATE ROLE "%s" LOGIN;""" % role.replace('\'', '\\\''))
                roles_added = roles_added + 1

    if config.REMOVE_LOGIN_ROLES_FROM_POSTGRES:
        for role in login_roles_to_drop:
            if args.dry_run:
                print("""DROP ROLE "%s";""" % role.replace('\'', '\\\''))
            else:
                cur.execute("""DROP ROLE "%s";""" % role.replace('\'', '\\\''))
                roles_dropped = roles_dropped + 1

    if have_work:
        if args.dry_run:
            print("COMMIT;")
        else:
            cur.execute("COMMIT;")
            cur.close()
            print("Roles added to Postgres:     %d" % roles_added)
            print("Roles dropped from Postgres: %d" % roles_dropped)
    else:
        print("No roles were added or dropped.")

