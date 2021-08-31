################################################################################
#
# pgldapsync
#
# Synchronise Postgres roles with users in an LDAP directory.
#
# Copyright 2018 - 2021, EnterpriseDB Corporation
#
################################################################################

"""pgldapsync package creation."""

import sys
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the requirements list for the current version of Python
with open('requirements.txt', 'r') as reqf:
    if sys.version_info[0] >= 3:
        required = reqf.read().splitlines()
    else:
        required = reqf.read().decode("utf-8").splitlines()

setuptools.setup(
    name="pgldapsync",
    version="1.0.0",
    author="Dave Page",
    author_email="dave.page@enterprisedb.com",
    description="Synchronise LDAP users to Postgres",
    license='PostgreSQL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enterprisedb/pgldapsync",
    packages=setuptools.find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: PostgreSQL License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['pgldapsync=pgldapsync.__init__:main'],
    },
    include_package_data=True
)
