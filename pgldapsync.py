#!/usr/bin/env python

################################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
################################################################################

# -*- coding: utf-8 -*-

"""pgldapsync application runner."""

# FIX THIS!
# pylint: disable=import-self

import re
import sys

from pgldapsync import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
