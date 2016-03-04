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

while True:
	data = get_BLE_data()
	print(data)
	time.sleep(1)