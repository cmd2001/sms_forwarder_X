#!/bin/bash
nmcli dev down wwan0qmi0
sleep 5
echo 'switching sim'
mmcli -m any --set-primary-sim-slot=1
echo 'restarting ModemManager'
systemctl stop ModemManager
qmicli -d /dev/wwan0qmi0 --uim-sim-power-off=1
qmicli -d /dev/wwan0qmi0 --uim-sim-power-on=1
systemctl start ModemManager
sleep 10
