#!/usr/bin/env python
#
# Module: vyatta-check-rfc-compatibility.py
#
# **** License ****
#
# # Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2016 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# Author: Lorenzo Martinico
# Date: June 2016
# Description: Script to print error message when RFC-compatibility is activated on VMware environments
#
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****

from vyatta import configd
import re, sys

client = configd.Client()
# Fetch vendor environment
version = client.call_rpc_dict("vyatta-opd-v1", "command", {"command":"show", "args":"version"})

if re.search(r'Hypervisor:\s*(\w+)',version['output']) is not None:
    vendor = re.search(r'Hypervisor:\s*(\w+)',version['output']).group(1)
else:
    vendor = "Unknown"

# vrrp_on set if vyatta-keepalived.pl passes an argument       
vrrp_on = len(sys.argv) > 1 

if vendor == "VMware" and vrrp_on:
    print("RFC compatibility is not supported on VMware\n")
