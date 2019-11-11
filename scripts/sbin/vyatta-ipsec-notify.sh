#!/bin/bash

# Script to reload (stop/restart) ipsec daemon upon
# VRRP state change

# **** License ****
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2014,2016 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# SPDX-License-Identifier: GPL-2.0-only
#

TYPE=$1
NAME=$2
STATE=$3

# check if there is a active L2TP/IPsec RA VPN server setup
L2TP_RAVPN=false
grep -qE '^\[global\]' /etc/xl2tpd/xl2tpd.conf 2> /dev/null && L2TP_RAVPN=true

case $STATE in
        "MASTER")
                  # in case charon was started via stroke earlier. To prevent service file failure.
                  ipsec stop || true

                  systemctl restart strongswan | logger -p info -t $(/usr/bin/basename $0)
                  $L2TP_RAVPN && systemctl restart xl2tpd | logger -p info -t $(/usr/bin/basename $0)
                  exit 0
                  ;;
        "BACKUP")
                  systemctl stop strongswan | logger -p info -t $(/usr/bin/basename $0)
                  $L2TP_RAVPN && systemctl stop xl2tpd | logger -p info -t $(/usr/bin/basename $0)
                  exit 0
                  ;;
        "FAULT")
                  systemctl stop strongswan | logger -p info -t $(/usr/bin/basename $0)
                  $L2TP_RAVPN && systemctl stop xl2tpd | logger -p info -t $(/usr/bin/basename $0)
                  exit 0
                  ;;
        *)        echo "unknown state"
                  exit 1
                  ;;
esac
