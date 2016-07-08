## Imports
import sys
import os
import time
import struct
import csv
import json
import datetime
import requests
import _thread

## Pre-reqs
os.system('hciconfig hci0 down')
os.system('hciconfig hci0 up')
time.sleep(2)
os.system('hciconfig hci0 up')

## Initialize variables
sensing_time = 1.5
name_to_match = "434c4152495459"
GPS = [-122.2689315, 37.8712693] #change this based on the position
sensors_found = []
fieldnames = ['time (sec)']

## Initialize BLE
from BLE_init import *

## Initialize File
folder_name = "/mnt/Clarity/ClarityData/"
num_file = len([f for f in os.listdir(folder_name)]) + 1
file_name = folder_name + "ClarityData" + str(num_file) + ".csv"
print(file_name)

## Save to file
def populate_fieldnames():
    for sensor in sensors_found:
        fieldnames.append(sensor + '_mc')
        fieldnames.append(sensor + '_nc')

def init_file():
    try:
        with open(file_name, "a") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            print('Readings at: ' + file_name)
    except:
        print('No USB drive found. File cannot be written')
        pass

def save_to_file(reading):
    try:
        with open(file_name, "a") as file_to_update:
            updater = csv.DictWriter(file_to_update, fieldnames=fieldnames)
            updater.writerow(reading)
    except:
        print('Writerow failed. No file to write on')
        pass

## Helper functions
def upload_to_cloud(data_to_upload):
    baseurl = "https://api.clarity.io/v2/measurements"
    time_now = datetime.datetime.utcnow().isoformat() + 'Z'

    for dev_id in sensors_found:
        json_to_upload = {}
        json_to_upload["recId"] = dev_id + "_" + time_now
        json_to_upload["device"] = "ffffffffffffffffffff" + dev_id
        json_to_upload["location"] = {"type":"Point","coordinates":GPS}
        json_to_upload["time"] = time_now
        json_to_upload["pm2_5"] = {"value":data_to_upload.get(dev_id + "_mc"), "raw":data_to_upload.get(dev_id + "_nc"), "estimatedAccuracy":10}
        try:
            f = requests.post(baseurl, json=json_to_upload)
        except:
            print('Upload failed, check internet connection')
    return

## Main loop to collect data
ctr = 0
start_time = time.time()
while True:
    if ctr < 1:
        loop_time = time.time()
        while time.time() - loop_time < sensing_time:
            data = get_BLE_raw()
            dev_id = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
            dev_name = str("".join("{0:02x}".format(x) for x in data[16:23:1]))
            if dev_name == name_to_match:
                if not dev_id in sensors_found:
                    sensors_found.append(dev_id)
        if not sensors_found:
            print('No sensors found')
        else:
            print('Sensors Found: ' + str(sensors_found))
            ctr += 1
            populate_fieldnames()
            init_file()
    else:
        loop_time = time.time()
        dev_readings = {}
        while time.time() - loop_time < sensing_time:
            data = get_BLE_raw()
            dev_id = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
            dev_name = str("".join("{0:02x}".format(x) for x in data[16:23:1]))
            if (dev_id in sensors_found) and (dev_name == name_to_match):
                num_conc = str(int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16))
                mass_conc = str(int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16))
                dev_readings[dev_id + "_nc"] = num_conc
                dev_readings[dev_id + "_mc"] = mass_conc
        dev_readings['time (sec)'] = int(time.time() - start_time)
        save_to_file(dev_readings)
        _thread.start_new_thread(upload_to_cloud, (dev_readings, ))