#!/bin/bash
target_free=$(awk -v percent="${used_memory_percent}" '/MemTotal/{printf "%d\n", $2 * (1.0-percent);}' < /proc/meminfo)
sudo ufw disable
sudo apt-get install -y snmpd
sudo service snmpd stop
echo "syslocation Unknown
syscontact Root <root@localhost>
dontLogTCPWrappersConnects yes
view CloudifyMonitoringView included .1.3.6.1.4.1.2021
createUser ${snmp_user} SHA ${snmp_pass} AES ${snmp_pass}
rouser ${snmp_user} priv -V CloudifyMonitoringView
disk / ${free_storage_percentage_threshold}
proc nginx
proc systemd
monitor -u ${snmp_user} -r 10 -o memTotalReal.0 -o memAvailReal.0 \"Real Memory\" memAvailReal.0 < ${target_free}
" | sudo tee /etc/snmp/snmpd.conf
sudo service snmpd restart
sudo systemctl enable snmpd
