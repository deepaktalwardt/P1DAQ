# Imports
import sys
import os
import time
import struct
import csv
from random import randint
import requests
import datetime
from collections import defaultdict
from THpythonLib import *
from BLE_init import *
from ubidots import ApiClient

# Variables

# Functions
##def known_sensor():
##    
##def get_sensor_reading():
##    to_return = 
##    data = get_BLE_raw():
##    BT_path = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
##    if known_sensor(str(BT_path)):
##        dev_id = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
##        num_conc = num_conc = int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16)
##        mass_conc = int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16)
##


# Loop to run
while True:
    data = get_BLE_raw()
    BT_path = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
    print(BT_path)
    
