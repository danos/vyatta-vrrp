#!/opt/vyatta/bin/cliexec
vyatta-keepalived.pl --vrrp-action delete --intf $VAR(../../@) --group $VAR(@)
