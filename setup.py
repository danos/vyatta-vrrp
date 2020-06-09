#!/usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import os
import re


import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

requirements = [
    "gi", "pydbus"
]


cwd = os.path.dirname(os.path.abspath(__file__))


def get_version():
    latest_ver: str
    with open(f"{cwd}/debian/changelog", "r") as fh:
        latest_ver = fh.readlines()[0]
        latest_ver = re.search(r"\((.*)\)", latest_ver).group(1)
    return f"{latest_ver}"


setuptools.setup(
    name="vyatta-vrrp-vci",
    version=get_version(),
    maintainer="Vyatta Package Maintainers",
    author_email="DL-vyatta-help@att.com",
    description=(
        "Vyatta Component Infrastructure module to configure "
        "VRRP on DANOS and it's derivatives"
    ),
    long_description=long_description,
    url="https://github.com/danos/vyatta-vrrp",
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        ("License :: OSI Approved :: "
         "GNU General Public License v2 (GPLv2)"),
    ],
    python_requires='>=3.6',
)
