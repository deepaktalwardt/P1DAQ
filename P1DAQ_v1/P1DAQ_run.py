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
#from ubidots import ApiClient
#from MQTTize import *
import Adafruit_MCP9808.MCP9808 as int_temp



############ Variables and Setup #############
## File Saving
# For P1DAQ Box 1
dev_ids = ["0009", "0011", "0020", "0027", "000c"]

dev_addrs = ["fd:9e:85:fe:57:ff",
             "ef:9b:60:f5:db:82",
             "f3:3d:9c:32:c4:c2",
             "e6:23:33:d8:5e:0d",
             "e9:6d:3d:79:17:c2"]

# For P1DAQ Box 2
# dev_ids = ["0001", "0010", "0016", "0024", "0032"]

# dev_addrs = ["cc:50:39:b3:b8:9a",
#              "cd:49:39:88:eb:79",
#              "ce:bb:b9:a4:0c:e7",
#              "e3:ce:c3:74:79:8d",
#              "fa:26:e0:1f:4e:61"]

fieldnames = [dev_ids[0] + "_mc", dev_ids[0] + "_nc", 
              dev_ids[1] + "_mc", dev_ids[1] + "_nc",
              dev_ids[2] + "_mc", dev_ids[2] + "_nc",
              dev_ids[3] + "_mc", dev_ids[3] + "_nc",
              dev_ids[4] + "_mc", dev_ids[4] + "_nc",
              "In Temp (deg C)", "Out Temp (deg C)",
              "Relative Humidity (%)",
              "Time (UT)"]

log_fieldnames = ['tn',
                  'sn',
                  'cid',
                  'cmd',
                  'arg',
                  'ts',
                  'es']

tz_dict = {'-11:00' :   'US/Samoa',
           '-10:00' :   'Pacific/Honolulu',
           '-09:00' :   'US/Alaska',
           '-08:00' :   'US/Pacific-New',
           '-07:00' :   'US/Mountain',
           '-06:00' :   'US/Central',
           '-05:00' :   'US/Eastern',
           '-04:00' :   'America/Antigua',
           '-03:00' :   'America/Araguaina',
           '-02:00' :   'Brazil/DeNoronha',
           '-01:00' :   'Atlantic/Cape_Verde',
           '+00:00' :   'Europe/London',
           '+01:00' :   'Africa/Windhoek',
           '+02:00' :   'Africa/Blantyre',
           '+03:00' :   'Africa/Addis_Adaba',
           '+04:00' :   'Asia/Baku',
           '+05:00' :   'Asia/Ashgabat',
           '+05:30' :   'Asia/Calcutta',
           '+06:00' :   'Indian/Chagos',
           '+07:00' :   'Indian/Christmas',
           '+08:00' :   'Singapore',
           '+09:00' :   'Asia/Dili',
           '+10:00' :   'Pacific/Yap',
           '+11:00' :   'Pacific/Bougainville'  
            } # Add half/quarter time zones

folder_name_1 = "/media/pi/Clarity/ClarityData/"
folder_name_2 = "/media/pi/Clarity/Logs/"

num_file_1 = len([f for f in os.listdir(folder_name_1)]) + 1
file_name_1 = folder_name_1 + "DataFile" + str(num_file_1) + ".csv"

num_file_2 = len([f for f in os.listdir(folder_name_2)]) + 1
file_name_2 = folder_name_2 + "LogFile" + str(num_file_2) + ".csv"

# Initialize Files to save readings and logs
with open(file_name_1, "a") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    print('Readings at: ' + file_name_1)

with open(file_name_2, "a") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=log_fieldnames)
    writer.writeheader()
    print('Logs at: ' + file_name_2)

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
PUBLIC_BROKER   =   "broker.hivemq.com"
TOPIC_DOWN      =   {} # populated later
SAMPLING_TIMES  =   {} # populated later
SERIAL_NUMBERS  =   {} # populated later
CURR_MASS_DATA  =   {} # populated later
CURR_NUM_DATA   =   {} # populated later

# Populate TOPIC_DOWN
for dev_id in DEVICE_IDS:
    TOPIC_DOWN[dev_id] = TOPIC_UP + '/' + dev_id

# Populate SAMPLING_TIMES
for dev_id in DEVICE_IDS:
    SAMPLING_TIMES[dev_id] = 1 # Default set to 1, can be changed later

### Remove this!!!!!
# SAMPLING_TIMES['c1c8'] = 2

# Populate SERIAL_NUMBERS
for dev_id in DEVICE_IDS:
    SERIAL_NUMBERS[dev_id] = dev_id # Serial Numbers refer to the Name

# Populate CURR_MASS_DATA
for dev_id in DEVICE_IDS:
    CURR_MASS_DATA.setdefault(dev_id, list())
print("Curr_Mass_init: " + str(CURR_MASS_DATA))

# Populate CURR_NUM_DATA
for dev_id in DEVICE_IDS:
    CURR_NUM_DATA.setdefault(dev_id, list())
print("Curr_Num_init: " + str(CURR_NUM_DATA))



############ Helper Functions ###############
## MQTT Clients Callback functions
# For client_1
def on_publish_1(client, userdata, mid):
    print("mid: " + str(mid))

def on_connect_1(client, data, flags, rc):
    print('Client 1 Connected, rc: ' + str(rc))

# For client_2
def on_message_1(client, userdata, msg):
    print('Command from ' + msg.topic + ' received')
    decode_command(msg.payload)
    # command_record(msg.payload)

def on_subscribe_1(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
 
# def on_connect_2(client, data, flags, rc):
#     print('Client 2 Connected, rc: ' + str(rc))

# def on_publish_2(client, data, flags, rc):
#     print('Command Published:' + str(mid))

## Sensor Data Acquisition functions
# Check if the ble_path is recognized
def known_sensor(ble_path):
    for dev_addr in dev_addrs:
        if dev_addr == ble_path:
            return True
    return False

# Checks and fixes the readings, replaces None with -1
def check_reading(reading):
    for key in reading.keys():
        if reading.get(key) == None:
            reading[key] = -1
    return reading

# Saves a row of readings to an already open file object
def save_to_file(reading, filename, fields):
    with open(filename, "a") as file_to_update:
        updater = csv.DictWriter(file_to_update, fieldnames = fields)
        updater.writerow(reading)

# Averages readings, truncated and not used anymore.
# def avg_readings(reading):
#     global counter
#     global readings_list
#     if counter < 1:
#         readings_list.append(reading)
#         return reading
#     else:
#         to_return = dict.fromkeys(fieldnames)
#         for k in readings_list[0].keys():
#             if not k == "Time (UT)":
#                 v = 0
#                 for r in readings_list:
#                     v += r.get(k)
#                 v = v/5
#                 to_return[k] = v
#             else:
#                 to_return[k] = readings_list[0].get(k)
#         counter = 0
#         return to_return

# Averages readings from a single sensor over a few seconds
def average_single_sensor(data, dev_id):
    if len(CURR_MASS_DATA.get(dev_id)) == 1:
        return (CURR_MASS_DATA[dev_id][0], CURR_NUM_DATA[dev_id][0])
    tot_mc = 0
    tot_nc = 0
    cnt_mc = 0
    cnt_nc = 0
    for mc in CURR_MASS_DATA[dev_id]:
        if mc >= 0:
            tot_mc = tot_mc + mc
            cnt_mc += 1
    for nc in CURR_NUM_DATA[dev_id]:
        if nc >= 0:
            tot_nc = tot_nc + nc 
            cnt_nc += 1
    if cnt_nc <= 0:
        cnt_nc = 1
    if cnt_mc <= 0:
        cnt_mc = 1
    avg_mc = int(tot_mc/cnt_mc)
    avg_nc = int(tot_nc/cnt_nc)
    data[dev_id + "_mc"] = avg_mc
    data[dev_id + "_nc"] = avg_nc
    return (avg_mc, avg_nc)

# Populates the variables: CURR_MASS_DATA, CURR_NUM_DATA everytime new reading
# is required.
def populate_curr_data(data):
    global CURR_MASS_DATA
    global CURR_NUM_DATA
    for dev_id in dev_ids:
        CURR_MASS_DATA[dev_id].append(data.get(dev_id + "_mc"))
        CURR_NUM_DATA[dev_id].append(data.get(dev_id + "_nc"))

# Increments sample number as it is sent to the broker
# def increment_sn(dev_id):
#     global SAMPLE_NUMBERS
#     SAMPLE_NUMBERS[dev_id] = SAMPLE_NUMBERS.get(dev_id) + 1

# Gets sensor readings as a dictionary from Bluetooth stack
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
    to_return["In Temp (deg C)"] = int_temp_sensor.readTempC()
    to_return["Out Temp (deg C)"] = float("%.*f" % (3, read_temperature())) 
    to_return["Relative Humidity (%)"] = float("%.*f" % (3, read_humidity())) 
    to_return["Time (UT)"] = datetime.datetime.now().isoformat()
    to_return = check_reading(to_return)
    print('Sensor Reading: ' + str(to_return))
    populate_curr_data(to_return)
    return to_return

## MQTT JSON Packets generation
# Generates Single sensor reading JSON to be sent to the MQTT Broker by client 1
def sensor_json(data, dev_id):
    # Increment SAMPLE_NUMBER to be sent
    # increment_sn(dev_id)

    # Initialize all JSONs
    to_send = {}
    d = {}
    psd = {}
    mc = {}

    # Generate variables
    t_n = DEVICE_TYPE + "-" + dev_id
    int_temp = data.get("In Temp (deg C)") # Change later to function call
    out_temp = data.get("Out Temp (deg C)") # Change later to function call
    out_humi = data.get("Relative Humidity (%)") # Change later to function call
    time_now = data.get("Time (UT)")
    air_flow = 1000 # Not sure if we need to change this
    sampling_time = SAMPLING_TIMES.get(dev_id) # May need to change later
    serial_number = SERIAL_NUMBERS.get(dev_id)

    # Generate Sub JSONs
    psd["unit"] = "cpcm3" # Counts per cm3
    psd["pm25num"] = data.get(dev_id + "_nc") #data.get(DEVICE_ID + "_nc")

    mc["unit"] = "ugpm3" # ug per m3
    mc["pm25conc"] = data.get(dev_id + "_mc") #data.get(DEVICE_ID + "_mc")

    d["tn"] = t_n
    d["sn"] = serial_number
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
    jsonized = json.dumps(to_send)
    #print('JSON packet sent: ' + jsonized)
    return jsonized

# Decode Command Response JSON
# Current commands include the following:
# cid: 1, cmd: set_st, arg: number of samples at 2.5 sec each
# cid: 2, cmd: get_st, arg: None, es: sampling time/fail
# cid: 3, cmd: set_clock, arg: time in isoformat+time difference to be added/subt
#     es: success/fail (Same for all sensors, cannot change individually)
# cid: 4, cmd: set_dev_id, arg: name in the correct format, es: success/fail
def decode_command(command):
    j_com = json.loads(str(command)[2:-1])
    tn = j_com.get('c').get('tn')
    print("tn: " + str(tn))
    sn = j_com.get('c').get('sn')
    cid = j_com.get('c').get('cid')
    cmd = j_com.get('c').get('cmd')
    arg = j_com.get('c').get('arg')
    print("arg: " + str(arg))
    ts = j_com.get('ts')
    if tn[-4:] in dev_ids:
        if cid == 1:
            if arg is not None:
                set_st(tn, sn, cid, cmd, arg)
            else:
                print('IGNORED')
        elif cid == 2:
            get_st(tn, sn, cid, cmd)
        elif cid == 3:
            if arg is not None:
                arg = arg[-6:]
                set_clock(tn, sn, cid, cmd, arg)
            else:
                print('IGNORED')
        elif cid == 4:
            if arg is not None:
                set_dev_name(tn, sn, cid, cmd, arg)
            else:
                print('IGNORED')
        else:
            not_recog_cmd(tn, sn, cid, cmd, arg)
    else:
        print('FAIL: Device ID (tn) not recognized.')
        pub_cmd_response(tn[-4:], tn, sn, cid, cmd, '', 'fail')

# Create Command Response JSON packet to be sent to the MQTT Broker by client 2
def cmd_resp_json(tn, sn, cid, cmd, es):
    # Initialize all JSONs
    to_send = {}
    c = {}

    # Populate individual JSONs
    c['tn'] = tn
    c['sn'] =  sn
    c['cid'] = cid
    c['cmd'] = cmd
    c['es'] = es

    ts = datetime.datetime.now().isoformat()

    to_send['c'] = c
    to_send['ts'] = ts
    return json.dumps(to_send)

## Command Execution functions
# Sets a new sampling time for the given device ID
def set_st(tn, sn, cid, cmd, arg):
    global SAMPLING_TIMES
    dev_id = tn[-4:]
    if cmd == 'set_st':
        if arg >= 2.5 and arg <= 3600:
            SAMPLING_TIMES[dev_id] = int(arg/2.5)
            print('Command Success')
            es = 'success'
            pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)
        else:
            print('FAIL: Sampling time not in range')
            es = 'fail'
            pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)
    else:
        print('FAIL: Command cmd does not match cid')
        es = 'fail'
        pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)

# Gets the sampling time for the given device number
def get_st(tn, sn, cid, cmd):
    dev_id = tn[-4:]
    if cmd == 'get_st':
        es = int(SAMPLING_TIMES[dev_id]*2.5)
        print('Command Success')
        pub_cmd_response(dev_id, tn, sn, cid, cmd, '', es)
    else:
        print('FAIL: Command cmd does not match cid')
        es = 'fail'
        pub_cmd_response(dev_id, tn, sn, cid, cmd, '', es)

# Sets the local clock timezone for the Raspberry Pi
def set_clock(tn, sn, cid, cmd, arg):
    dev_id = tn[-4:]
    if cmd == 'set_clock':
        new_tz = tz_dict[arg]
        if arg in tz_dict:
            os.environ['TZ'] = new_tz
            time.tzset()
            es = 'success'
            pub_cmd_response(dev_id, tn, sn, cid, cmd, '', es)
        else:
            print('FAIL: Timezone not supported')
            es = 'fail'
            pub_cmd_response(dev_id, tn, sn, cid, cmd, '', es)
    else:
        print('FAIL: Command cmd does not match cid')
        es = 'fail'
        pub_cmd_response(dev_id, tn, sn, cid, cmd, '', es)

# Resets the device name (serial number) for the device
def set_dev_name(tn, sn, cid, cmd, arg):
    global SERIAL_NUMBERS
    dev_id = tn[-4:]
    if cmd == 'set_dev_name':
        SERIAL_NUMBERS[dev_id] = arg
        es = 'success'
        pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)
    else:
        print('FAIL: Command cmd does not match cid')
        es = 'fail'
        pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)

# Sends a fail execution status if the cid is not recognized
def not_recog_cmd(tn, sn, cid, cmd, arg):
    print('FAIL: Command not recognized')
    dev_id = tn[-4:]
    es = 'fail'
    pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es)

# Save commands to a file for record
def command_record(command, arg):
    to_save = {}
    j_com = json.loads(str(command))
    tn = j_com.get('c').get('tn')
    sn = j_com.get('c').get('sn')
    cid = j_com.get('c').get('cid')
    cmd = j_com.get('c').get('cmd')
    es = j_com.get('c').get('es')
    ts = j_com.get('ts')

    to_save['tn'] = tn
    to_save['sn'] = sn
    to_save['cid'] = cid
    to_save['cmd'] = cmd
    to_save['arg'] = arg
    to_save['ts'] = ts
    to_save['es'] = es

    save_to_file(to_save, file_name_2, log_fieldnames)


## MQTT Publishing functions
# Publish Sensor Reading
def pub_sensor_reading(sensor_data):
    global CURR_MASS_DATA
    global CURR_NUM_DATA
    for DEVICE_ID in DEVICE_IDS:
        if len(CURR_MASS_DATA.get(DEVICE_ID)) >= SAMPLING_TIMES.get(DEVICE_ID):
            avgd_data = average_single_sensor(sensor_data, DEVICE_ID)
            print(avgd_data)
            sensor_data[DEVICE_ID + "_mc"] = avgd_data[0]
            sensor_data[DEVICE_ID + "_nc"] = avgd_data[1]
            client_1.publish(TOPIC_UP, sensor_json(sensor_data, DEVICE_ID), qos=1)
            CURR_NUM_DATA[DEVICE_ID] = []
            CURR_MASS_DATA[DEVICE_ID] = []

# Publish Command Response
def pub_cmd_response(dev_id, tn, sn, cid, cmd, arg, es):
    jsonized = cmd_resp_json(tn, sn, cid, cmd, es)
    dev_id = tn[-4:]
    client_1.publish(TOPIC_DOWN[dev_id], jsonized, qos=1)
    command_record(jsonized, arg)

# Setup MQTT Clients
client_1                =   paho.Client(client_id="d-" + ORG_ID + "-" + DEVICE_TYPE)
client_1.on_publish     =   on_publish_1
client_1.on_connect     =   on_connect_1
client_1.on_message     =   on_message_1
client_1.on_subscribe   =   on_subscribe_1
#client_1.username_pw_set(USERNAME, PASSWORD)

#client_2                =   paho.Client(client_id='P1DAQ_controls')
#client_2.on_message     =   on_message_2
#client_2.on_subscribe   =   on_subscribe_2
#client_2.on_connect     =   on_connect_2
#client_2.on_publish     =   on_publish_2
#client_2.username_pw_set(USERNAME, PASSWORD)

con = True
while con:
    try:
        client_1.connect(PUBLIC_BROKER, port=1883)
        con = False
    except:
        print('Retry connection')
        client_1.connect(PUBLIC_BROKER, port=1883)

#client_2.connect_async(PUBLIC_BROKER, port=1883)
#client_2.loop_start()

for DEVICE_ID in DEVICE_IDS:
    client_1.subscribe(TOPIC_DOWN[DEVICE_ID], qos=1)

loop = True
while loop:
    try:
        client_1.loop_start()
        loop = False
    except:
        print('Retry loop')
        client_1.loop_start()
#for i in range(0,6):
#for i in range(0,1000):
while True:
    readings = get_sensor_reading()
    save_to_file(readings, file_name_1, fieldnames)
    print('Curr_Mass: ' + str(CURR_MASS_DATA))
    print('Curr_Num: ' + str(CURR_NUM_DATA))
    pub_sensor_reading(readings)
    print('----------------------------------------------------')