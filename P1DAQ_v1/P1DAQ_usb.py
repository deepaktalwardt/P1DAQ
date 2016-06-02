# Data collection only on the usb
import os
import time
import csv
import Adafruit_MCP9808.MCP9808 as int_temp
import datetime
from THpythonLib import *
from BLE_init import *

dev_ids = ["0012", "000e", "0009", "0020", "000f"]

dev_addrs = ["dd:19:ae:49:ae:d3",
            "cd:3f:6c:1c:7d:d5",
            "fd:9e:85:fe:57:ff",
            "f3:3d:9c:32:c4:c2",
            "e3:35:be:3c:db:1f"]

fieldnames = [dev_ids[0] + "_mc", dev_ids[0] + "_nc", 
              dev_ids[1] + "_mc", dev_ids[1] + "_nc",
              dev_ids[2] + "_mc", dev_ids[2] + "_nc",
              dev_ids[3] + "_mc", dev_ids[3] + "_nc",
              dev_ids[4] + "_mc", dev_ids[4] + "_nc",
              "In Temp (deg C)", "Out Temp (deg C)",
              "Relative Humidity (%)",
              "Time"]

density = 1.9


folder_name_1 = "/mnt/Clarity/ClarityData/"

num_file_1 = len([f for f in os.listdir(folder_name_1)]) + 1
file_name_1 = folder_name_1 + "DataFile" + str(num_file_1) + ".csv"

try:
    with open(file_name_1, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print('Readings at: ' + file_name_1)
except:
    print('No USB drive found. File cannot be written')
    pass

## Internal Temperature Sensor Initialize
try:
    int_temp_sensor = int_temp.MCP9808()
    int_temp_sensor.begin()
except:
    pass

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
    try:
        with open(filename, "a") as file_to_update:
            updater = csv.DictWriter(file_to_update, fieldnames = fields)
            updater.writerow(reading)
    except:
        print('Writerow failed. No file to write on')
        pass

# Gets sensor readings as a dictionary from Bluetooth stack
def get_sensor_reading():
    to_return = dict.fromkeys(fieldnames)
    start_time = time.time()
    while (time.time() - start_time) < 1.5:
        data = get_BLE_raw()
        ble_path = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
        if known_sensor(str(ble_path)):
            dev_id = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
            num_conc = int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16)
            mass_conc = int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16)
            mass_conc = int(density*mass_conc)
            to_return[dev_id + "_nc"] = num_conc
            to_return[dev_id + "_mc"] = mass_conc
    try:
        to_return["In Temp (deg C)"] = int_temp_sensor.readTempC()
    except:
        to_return["In Temp (deg C)"] = -1
    to_return["Out Temp (deg C)"] = float("%.*f" % (3, read_temperature())) 
    to_return["Relative Humidity (%)"] = float("%.*f" % (3, read_humidity())) 
    to_return["Time"] = datetime.datetime.now().isoformat()
    to_return = check_reading(to_return)
    print('Sensor Reading: ' + str(to_return))
    return to_return

while True:
    readings = get_sensor_reading()
    save_to_file(readings, file_name_1, fieldnames)
    print(readings)
    print('----------------------------------------------------')