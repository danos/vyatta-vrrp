#!/bin/sh

# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

if [ -e /var/run/vrrpd/changes ]; then
    echo "Leftover VRRP changes file detected - This is a bug" |
        systemd-cat -t vyatta-vrrp -p err
    cat /var/run/vrrpd/changes | systemd-cat -t vyatta-vrrp -p err
    rm /var/run/vrrpd/changes
fi
