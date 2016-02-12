import sys
import os
import time
import struct
import csv
import datetime
import binascii
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
# folderName = "/home/pi/ClarityData/"
folderName = "/media/pi/ClarityDataStorageDrive1/"
tnow = datetime.datetime.now().isoformat()
fixedTime = tnow[0:10] + "--" + tnow[11:13] + "-" + tnow[14:16] + "-" + tnow[17:19]
fileName = folderName + fixedTime + "ClarityData.csv"
recDevIDs = ["c1ba", "c1b5"]

#fieldnames = ['time(sec)','time_stamp','be7a_nc',
              #'be7a_mc','se01_nc', 'se01_mc']
fieldnames = ['time(sec)', 'time_stamp',
              recDevIDs[0] + "_nc", recDevIDs[0] + "_mc",
              recDevIDs[1] + "_nc", recDevIDs[1] + "_mc"]
              
#recDevAddr = ["f9:b1:23:8d:60:b1", "f1:59:2f:10:71:26"]
recDevAddr = ["d1:8d:3e:65:b1:4e", "e6:17:84:42:8a:d0",
              "db:70:86:13:64:02", "c9:a7:e6:4c:2a:02",
              "d0:4f:18:a1:b8:5c"]

nameToMatch = "434c4152495459" #CLARITY in hex

addrToDev = dict.fromkeys(recDevAddr, recDevIDs)
#devReadings = dict.fromkeys(fieldnames)
devReadings = {}

# Open a new file to write to
# with open(fileName, "a") as csvfile:
#     #fieldnames = ['be7a', 'de01']
#     writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
#     writer.writeheader()
    
# Check data and return corrected dictionary
def checkData(data):
    dataCopy = data
    for key in dataCopy.keys():
        if dataCopy.get(key) == None:
            dataCopy[key] = -1
    return dataCopy

# Check if the scanned device is recognized
def isRecDev(address):
    for devAdd in recDevAddr:
        if devAdd == address:
            return True
    return False
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

# Open the file to update

counter = 1;
dataTime = time.time()
while True:
    startTime = time.time()
    while (time.time() - startTime) < 2.5:
        data = sock.recv(1024)
        arr = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
        devName = str(''.join("{0:02x}".format(x) for x in data[16:23:1]))
        #print(devName)
        if devName == nameToMatch:
            devID = str("".join("{0:02x}".format(x) for x in data[31:29:-1]))
            if (counter == 1 or (devReadings.has_key(devID + "_nc"))):
                #print(devID)
                #reading = str("".join("{0:02x}".format(x) for x in data[39:30:-1]))
                num_conc = str(int("".join("{0:02x}".format(x) for x in data[33:31:-1]),16))
                mass_conc = str(int("".join("{0:02x}".format(x) for x in data[35:33:-1]),16))
                #batt_val = str(int("".join("{0:02x}".format(x) for x in data[36:35:-1]),16))
                #err_code = str(int("".join("{0:02x}".format(x) for x in data[37:36:-1]),16))
                devReadings[devID + "_nc"] = num_conc
                devReadings[devID + "_mc"] = mass_conc
    devReadings['time(sec)'] = time.time() - dataTime
    #devReadings['time_stamp'] = time.strftime("%c")
    toSave = checkData(devReadings)
    if counter == 1:
        with open(fileName, "a") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = devReadings.keys())
            writer.writeheader()
    with open(fileName, "a") as fileToUpdate:
        updater = csv.DictWriter(fileToUpdate, fieldnames = devReadings.keys())
        updater.writerow(toSave)
    counter += 1
    #print(str(devReadings))

              
