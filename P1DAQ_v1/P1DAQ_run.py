############### Import dependencies ################
import sys
import os
import time
import struct
import csv
import json
import paho.mqtt.client as paho
from random import randint
import requests
import datetime
from collections import defaultdict
from THpythonLib import *
from BLE_init import *
from ubidots import ApiClient
#from MQTTize import *
import Adafruit_MCP9808.MCP9808 as int_temp


############ Variables and Setup #############
## File Saving
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
              "In Temp (deg C)", "Out Temp (deg C)",
              "Relative Humidity (%)",
              "Time (UT)"]

folder_name = "/media/pi/Clarity/ClarityData/"
num_file = len([f for f in os.listdir(folder_name)]) + 1
file_name = folder_name + "DataFile" + str(num_file) + ".csv"

# Initialize File to save
with open(file_name, "a") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

## Internal Temperature Sensor Initialize
int_temp_sensor = int_temp.MCP9808()
int_temp_sensor.begin()

## MQTT Variables
ORG_ID          =   "CLMTCO"
DEVICE_TYPE     =   "P1"
DEVICE_IDS      =   dev_ids
USERNAME        =   "sensoriot"              
PASSWORD        =   "sensoriot"           
TOPIC_UP        =   "iot/SSRIOT/" + DEVICE_TYPE 
TOPIC_DOWN      =   {} # populated later
SAMPLING_TIMES  =   {} # populated later
SAMPLE_NUMBERS  =   {} # populated later
CURR_MASS_DATA  =   {} # populated later
CURR_NUM_DATA   =   {} # populated later

# Populate TOPIC_DOWN
for dev_id in DEVICE_IDS:
    TOPIC_DOWN[dev_id] = TOPIC_UP + '/' + dev_id

# Populate SAMPLING_TIMES
for dev_id in DEVICE_IDS:
    SAMPLING_TIMES[dev_id] = 1 # Default set to 1, can be changed later

# Populate SAMPLE_NUMBERS
for dev_id in DEVICE_IDS:
    SAMPLE_NUMBERS[dev_id] = 0 # Increments only after reading is published

# Populate CURR_DATA
for dev_id in DEVICE_IDS:
    CURR_DATA[dev_id] = []

# Setup MQTT Clients
client_1                =   paho.Client(client_id='P1DAQ_readings')
client_1.on_publish     =   on_publish_1
client_1.on_connect     =   on_connect_1
#client_1.username_pw_set(USERNAME, PASSWORD)

client_2                =   paho.Client(client_id='P1DAQ_controls')
client_2.on_message     =   on_message_2
client_2.on_subscribe   =   on_subscribe_2
client_2.on_connect     =   on_connect_2
#client_2.username_pw_set(USERNAME, PASSWORD)

############ Helper Functions ###############
## MQTT Clients Callback functions
# For client_1
def on_publish_1(client, userdata, mid):
    print("mid: " + str(mid))

def on_connect_1(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))

# For client_2
def on_message_2(client, userdata, mid):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
 
def on_connect_2(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))

## Sensor Data Acquisition functions
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

def avg_readings(reading):
    global counter
    global readings_list
    if counter < 1:
        readings_list.append(reading)
        return reading
    else:
        to_return = dict.fromkeys(fieldnames)
        for k in readings_list[0].keys():
            if not k == "Time (UT)":
                v = 0
                for r in readings_list:
                    v += r.get(k)
                v = v/5
                to_return[k] = v
            else:
                to_return[k] = readings_list[0].get(k)
        counter = 0
        return to_return

def average_single_reading(data, dev_id):
    if len(data.get(dev_id + "_mc")) == 1:
        data[dev_id + "_mc"] = data.get(dev_id + "_mc")[0]
        data[dev_id + "_nc"] = data.get(dev_id + "_nc")[0]
        return data
    tot_mc = 0
    tot_nc = 0
    cnt_mc = 0
    cnt_nc = 0
    for mc in data.get(dev_id + "_mc"):
        if mc >= 0:
            tot_mc = tot_mc + mc
            cnt_mc += 1
    for nc in data.get(dev_id + "_nc"):
        if nc >= 0:
            tot_nc = tot_nc + nc 
            cnt_nc += 1
    avg_mc = tot_mc/cnt_mc
    avg_nc = tot_nc/cnt_nc
    data[dev_id + "_mc"] = avg_mc
    data[dev_id + "_nc"] = avg_nc
    return data

def populate_curr_data(data):
    global CURR_MASS_DATA
    global CURR_NUM_DATA
    for dev_id in dev_ids:
        CURR_MASS_DATA[dev_id] = CURR_MASS_DATA.get(dev_id).append(data.get(dev_id + "_mc"))
        CURR_NUM_DATA[dev_id] = CURR_NUM_DATA.get(dev_id).append(data.get(dev_id + "_nc"))

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
    to_return["In Temp (deg C)"] = int_temp_sensor.readTempC() # Change this later to a function call
    to_return["Out Temp (deg C)"] = read_temperature() # Change this later to a function call
    to_return["Relative Humidity (%)"] = read_humidity() # Change this later to a function call
    to_return["Time (UT)"] = datetime.datetime.now().isoformat()
    to_return = check_reading(to_return)
    populate_curr_data(to_return)
    return to_return

## MQTT JSON Packets generation

# Single sensor reading JSON
def sensor_json(data, dev_id):
    # Increment SAMPLE_NUMBER to be sent
    increment_sn(dev_id)

    # Initialize all JSONs
    to_send = {}
    d = {}
    psd = {}
    mc = {}

    # Generate variables
    t_n = "d-" + ORG_ID + "-" + DEVICE_TYPE + "-" + dev_id
    int_temp = data.get("In Temp (deg C)") # Change later to function call
    out_temp = data.get("Out Temp (deg C)") # Change later to function call
    out_humi = data.get("Relative Humidity (%)") # Change later to function call
    time_now = data.get("Time (UT)")
    air_flow = 1000 # Not sure if we need to change this
    sampling_time = SAMPLING_TIMES.get(dev_id) # May need to change later
    sample_number = SAMPLE_NUMBERS.get(dev_id)

    # Generate Sub JSONs
    psd["unit"] = "cpcm3" # Counts per cm3
    psd["pm25num"] = data.get(dev_id + "_nc") #data.get(DEVICE_ID + "_nc")

    mc["unit"] = "ugpm3" # ug per m3
    mc["pm25conc"] = data.get(dev_id + "_mc") #data.get(DEVICE_ID + "_mc")

    d["tn"] = t_n
    d["sn"] = sample_number
    d["st"] = sampling_time
    d["psd"] = psd
    d["mc"] = mc
    d["af"] = air_flow
    d["it"] = int_temp
    d["ot"] = out_temp
    d["oh"] = out_humi

    # Generate to_send JSON
    to_send["d"] = d
    to_send["ts"] = time_now
    return json.dumps(to_send)

# Command JSON decode

# Command Response JSON 

## MQTT Publishing functions
# Publish Sensor Reading
def pub_sensor_reading(data):
    global CURR_MASS_DATA
    global CURR_NUM_DATA
    for DEVICE_ID in DEVICE_IDS:
        to_JSON = {}
        if len(CURR_MASS_DATA.get(DEVICE_ID)) >= SAMPLING_TIMES.get(DEVICE_ID):
            to_JSON[DEVICE_ID + "_mc"] = CURR_MASS_DATA.get(DEVICE_ID)
            to_JSON[DEVICE_ID + "_nc"] = CURR_NUM_DATA.get(DEVICE_ID)
            to_JSON["In Temp (deg C)"] = data.get("In Temp (deg C)")
            to_JSON["Out Temp (deg C)"] = data.get("Out Temp (deg C)")
            to_JSON["Relative Humidity (%)"] = data.get("Relative Humidity (%)")
            to_JSON["Time (UT)"] = data.get("Time (UT)")
            avgd_data = average_single_reading(to_JSON, dev_id)
            client_1.publish(TOPIC_UP, sensor_json(avgd_data, DEVICE_ID), qos=1)

# Publish Command Response


## Command Setting functions
def set_st(dev_id, new_st):
    global SAMPLING_TIMES
    SAMPLING_TIMES[dev_id] = new_st

def increment_sn(dev_id):
    global SAMPLE_NUMBERS
    SAMPLE_NUMBERS[dev_id] = SAMPLE_NUMBERS.get(dev_id) + 1

