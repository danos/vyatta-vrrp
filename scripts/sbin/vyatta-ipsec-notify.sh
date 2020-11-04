#!/bin/vcli -f

# Script to reload (stop/restart) ipsec daemon upon
# VRRP state change

# **** License ****
# Copyright (c) 2019-2020 AT&T Intellectual Property.
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

case $STATE in
        "MASTER")
                  # in case charon was started via stroke earlier. To prevent service file failure.
                  # only needed when the script using IPsec stroke is present.
                  if [ -f /opt/vyatta/sbin/vpn-config.pl ]; then
                          ipsec stop || true
                          run restart vpn | logger -p info -t $(/usr/bin/basename $0)
                  else
                          /lib/vci-security-vpn-ipsec/ipsec-op restart-vpn | logger -p info -t $(/usr/bin/basename $0)
                  fi
                  exit 0
                  ;;
        "BACKUP")
                  systemctl kill -s TERM strongswan | logger -p info -t $(/usr/bin/basename $0)
                  exit 0
                  ;;
        "FAULT")
                  systemctl kill -s TERM strongswan | logger -p info -t $(/usr/bin/basename $0)
                  exit 0
                  ;;
        *)        echo "unknown state"
                  exit 1
                  ;;
esac
