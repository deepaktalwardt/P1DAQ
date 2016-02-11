#!/bin/sh
# launcher.sh

cd /
cd home/pi/ClarityCode
sudo hciconfig hci0 up
sudo pigpiod
sudo python3 enumerateBLE.py
cd /