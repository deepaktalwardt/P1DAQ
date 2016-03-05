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
dev_ids = ["c1c3", "c1c8", "c1c9", "c1b2", "c1b4"]

dev_addrs = ["fa:c8:d9:40:4e:81",
             "d8:3c:9b:90:f3:d9",
             "f3:8f:db:af:9a:45",
             "d5:07:7e:65:e7:45",
             "ed:3c:d4:9c:ff:74"]

fieldnames = [dev_ids[0] + "_mc", dev_ids[0] + "_nc", 
              dev_ids[1] + "_mc", dev_ids[1] + "_nc",
              dev_ids[2] + "_mc", dev_ids[2] + "_nc",
              dev_ids[3] + "_mc", dev_ids[3] + "_nc",
              dev_ids[4] + "_mc", dev_ids[4] + "_nc",
              "In Temp (deg C)", "Out Temp (deg C)"
              "Relative Humidity (%)",
              "Time (UT)"]

readings_list = []

folder_name = "/media/pi/Clarity/ClarityData/"
num_file = len([f for f in os.listdir(folder_name)]) + 1
file_name = folder_name + "DataFile" + str(num_file) + ".csv"

with open(file_name, "a") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()

# Functions
def known_sensor(ble_path):
    for dev_addr in dev_addrs:
        if dev_addr == ble_path:
            return True
    return False

def check_reading(reading):
    for key in reading.keys():
        if reading.get(key) == None:
            reading[key] = -1
    return reading

def save_to_file(reading):
    with open(file_name, "a") as file_to_update:
        updater = csv.DictWriter(file_to_update, fieldnames = fieldnames)
        updater.writerow(reading)

def get_sensor_reading():
    to_return = dict.fromkeys(fieldnames)
    start_time = time.time()
    while (time.time() - start_time) < 2.5:
        data = get_BLE_raw()
        ble_path = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
        if known_sensor(str(ble_path)):
            dev_id = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
            num_conc = int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16)
            mass_conc = int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16)
            to_return[dev_id + "_nc"] = num_conc
            to_return[dev_id + "_mc"] = mass_conc
    to_return["In Temperature (deg C)"] = 23 # Change this later to a function call
    to_return["Out Temperature (deg C)"] = 27 # Change this later to a function call
    to_return["Relative Humidity (%)"] = 40 # Change this later to a function call
    to_return["Time (UT)"] = datetime.datetime.now().isoformat()
    to_return = check_reading(to_return)
    return to_return

# Loop to run
while True:
    readings = get_sensor_reading()
    save_to_file(readings)
    print("Saved: " + readings)
    