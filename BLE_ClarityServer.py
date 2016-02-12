# Uploaded from my computer!!!
import sys
import os
import time
import struct
import csv
os.environ['http_proxy'] = ''
import requests
import datetime
from collections import defaultdict
from THpythonLib import *
from ubidots import ApiClient
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
from socket import (
    socket,
    AF_BLUETOOTH,
    SOCK_RAW,
    BTPROTO_HCI,
    SOL_HCI,
    HCI_FILTER,
)
###############################################################
folderName = "/home/pi/ClarityData/"
#folderName = "/media/pi/UMIANCIAL/ClarityData/"
tnow = datetime.datetime.now().isoformat()
fixedTime = tnow[0:10] + "--" + tnow[11:13] + "-" + tnow[14:16] + "-" + tnow[17:19]
fileName = folderName + fixedTime + "ClarityData.csv"
recDevIDs = ["c101", "c102", "c103", "c104", "c105"]
print(fileName)

#fieldnames = ['time(sec)','time_stamp','be7a_nc',
              #'be7a_mc','se01_nc', 'se01_mc']
fieldnames = ['time(sec)', 'time_stamp',
              recDevIDs[0] + "_nc", recDevIDs[0] + "_mc",
              recDevIDs[1] + "_nc", recDevIDs[1] + "_mc",
              recDevIDs[2] + "_nc", recDevIDs[2] + "_mc",
              recDevIDs[3] + "_nc", recDevIDs[3] + "_mc",
              recDevIDs[4] + "_nc", recDevIDs[4] + "_mc",
              "Temperature (deg C)",
              "Relative Humidity (%)"]
              
#recDevAddr = ["f9:b1:23:8d:60:b1", "f1:59:2f:10:71:26"]
recDevAddr = ["d1:8d:3e:65:b1:4e", "e6:17:84:42:8a:d0",
              "db:70:86:13:64:02", "c9:a7:e6:4c:2a:02",
              "d0:4f:18:a1:b8:5c"]
addrToDev = dict.fromkeys(recDevAddr, recDevIDs)
#devReadings = dict.fromkeys(fieldnames)
#devReadings = {k:[] for k in fieldnames}
devReadings = {}

def initDevReadings():
    for key in fieldnames:
        devReadings.setdefault(key, [])
initDevReadings()

fileReadings = dict.fromkeys(fieldnames)
################################################################
# Clarity Cloud
baseurl = "https://api.joinclarity.io/v2/measurements"

def toClarityCloud(data):
    for i in range(1,6):
        dictToSend = {}
        devID = "c10" + str(i)
        dictToSend["device"] = "ffffffffffffffffffff" + devID
        dictToSend["location"] = {"type":"Point", "coordinates":[-122.2579268, 37.8749026]}
        dictToSend["time"] = datetime.datetime.now().isoformat()
        dictToSend["pm2_5"] = {"value": data.get(devID + "_mc"), "raw": data.get(devID + "_nc"), "estimatedAccuracy": 10}
        dictToSend["recId"] = devID + "_" + datetime.datetime.now().isoformat()
        sendRequest = requests.post(baseurl, json=dictToSend)
        print(dictToSend)
        print(sendRequest.status_code)

################################################################
try:
    clarityAPI = ApiClient("2331f6fb5568a0de255024aa024b2ec20f2e6e1d");
    c101 = clarityAPI.get_variable("56a00b1976254252dfa19fa8");
    c102 = clarityAPI.get_variable("56a00b5776254254a47b1bbc");
    c103 = clarityAPI.get_variable("56a00b6276254253988bc701");
    c104 = clarityAPI.get_variable("56a00b6d7625425626da050e");
    c105 = clarityAPI.get_variable("56a00b7876254254a47b1c1a");
    tsensor = clarityAPI.get_variable("56aab6647625422dfd956173");
    hsensor = clarityAPI.get_variable("56aab72b762542308ac08d6a"); 
except:
    print("Check your internet connection")

# Open a new file to write to
with open(fileName, "a") as csvfile:
    #fieldnames = ['be7a', 'de01']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    
# Check data and return corrected dictionary
def checkData(data):
    dataCopy = data
    for key in dataCopy.keys():
        if dataCopy.get(key) == None :
            dataCopy[key] = -1
        if dataCopy.get(key) == []:
            dataCopy[key] = [-1]
##        if isinstance(dataCopy[key], int):
##            dataCopy[key] = dataCopy.get(key)[-1]
    return dataCopy

# Average Values in a dict
def averageDict(dictToAvg):
    dataCopy = dictToAvg
    for key in dictToAvg.keys():
        if key != "time(sec)" and key != "time_stamp":
            dataCopy[key] = int(sum(dataCopy.get(key))/len(dataCopy.get(key)))
    return dataCopy

# Check if the scanned device is recognized
def isRecDev(address):
    for devAdd in recDevAddr:
        if devAdd == address:
            return True
    return False

# Upload Data to Ubidots
def saveOnUbidots(dictToSave):
    c101.save_value({'value':devReadings.get(recDevIDs[0] + "_mc")})
    c102.save_value({'value':devReadings.get(recDevIDs[1] + "_mc")})
    c103.save_value({'value':devReadings.get(recDevIDs[2] + "_mc")})
    c104.save_value({'value':devReadings.get(recDevIDs[3] + "_mc")})
    c105.save_value({'value':devReadings.get(recDevIDs[4] + "_mc")})
    tsensor.save_value({'value':devReadings.get("Temperature (deg C)")})
    hsensor.save_value({'value':devReadings.get("Relative Humidity (%)")})

# Reconnect to Ubidots if needed
def reconnectUbidots():
    clarityAPI = ApiClient("2331f6fb5568a0de255024aa024b2ec20f2e6e1d");
    c101 = clarityAPI.get_variable("56a00b1976254252dfa19fa8");
    c102 = clarityAPI.get_variable("56a00b5776254254a47b1bbc");
    c103 = clarityAPI.get_variable("56a00b6276254253988bc701");
    c104 = clarityAPI.get_variable("56a00b6d7625425626da050e");
    c105 = clarityAPI.get_variable("56a00b7876254254a47b1c1a");
    connTimer = time.time()
################################################################

if not os.geteuid() == 0:
    sys.exit("script only works as root")

btlib = find_library("bluetooth")
if not btlib:
    raise Exception(
        "Can't find required bluetooth libraries"
        " (need to install bluez)"
    )
bluez = CDLL(btlib, use_errno=True)

dev_id = bluez.hci_get_route(None)

sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
sock.bind((dev_id,))

err = bluez.hci_le_set_scan_parameters(sock.fileno(), 0, 0x10, 0x10, 0, 0, 1000);
if err < 0:
    raise Exception("Set scan parameters failed")
    # occurs when scanning is still enabled from previous call

# allows LE advertising events
hci_filter = struct.pack(
    "<IQH", 
    0x00000010, 
    0x4000000000000000, 
    0
)
sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)

err = bluez.hci_le_set_scan_enable(
    sock.fileno(),
    1,  # 1 - turn on;  0 - turn off
    0, # 0-filtering disabled, 1-filter out duplicates
    1000  # timeout
)
if err < 0:
    errnum = get_errno()
    raise Exception("{} {}".format(
        errno.errorcode[errnum],
        os.strerror(errnum)
    ))

# Connection Timer
connTimer = time.time()
failCounter = 0
while True:
    avgTime = time.time()
    while (time.time() - avgTime) < 10:
        startTime = time.time()
        while (time.time() - startTime) < 2.5:
            data = sock.recv(1024)
            BTpath = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
            if isRecDev(str(BTpath)):
                devID = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
                #reading = str("".join("{0:02x}".format(x) for x in data[39:30:-1]))
                num_conc = int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16)
                mass_conc = int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16)
                #batt_val = str(int("".join("{0:02x}".format(x) for x in data[36:35:-1]),16))
                #err_code = str(int("".join("{0:02x}".format(x) for x in data[37:36:-1]),16))
                devReadings[devID + "_nc"].append(num_conc)
                devReadings[devID + "_mc"].append(mass_conc)
                fileReadings[devID + "_nc"] = num_conc
                fileReadings[devID + "_mc"] = mass_conc
        temp = read_temperature()
        humi = read_humidity()
        currTime = time.time()
        currTimeText = time.strftime("%c")
        devReadings['Temperature (deg C)'].append(temp)
        devReadings['Relative Humidity (%)'].append(humi)
        devReadings['time(sec)'] = currTime
        devReadings['time_stamp'] = currTimeText
        fileReadings['time(sec)'] = currTime
        fileReadings['time_stamp'] = currTimeText
        fileReadings['Temperature (deg C)'] = temp
        fileReadings['Relative Humidity (%)'] = humi
        #print(fileReadings)
        toSave = checkData(fileReadings)
        devChecked = checkData(devReadings)
        with open(fileName, "a") as fileToUpdate:
            updater = csv.DictWriter(fileToUpdate, fieldnames = fieldnames)
            updater.writerow(toSave)
    devChecked = checkData(devReadings)
    avgdReadings = averageDict(devChecked)
    #print('-------------------------------')
    #print(avgdReadings)
    #saveOnUbidots(recDevIDs)
    try:
        toClarityCloud(avgdReadings)
    except:
        print("--------------Upload Failed: Trying again--------------")
        failCounter += 1
    devReadings = {}
    for key in fieldnames:
        devReadings.setdefault(key, [])
##    if (time.time() - connTimer) > 750:
##        reconnectUbidots()
    print("fails: " + str(failCounter) + "--------------")
    #print(str(devReadings))

              
