#!/bin/sh
# LocalLoggingLauncher.sh

cd /
cd home/pi/P1DAQ/LocalLoggingNoTH
sleep 30s
sudo hciconfig hci0 up
sudo python3 P1DAQ_BLE_AEPA.py
cd /
