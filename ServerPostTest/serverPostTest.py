import json
import datetime
import requests
import time
import random

baseurl = "https://api.clarity.io/v2/measurements"
devID = "0002"
pm = random.randint(0,500)

for i in range(0,10):
    
    dataStorage = {}
    dataStorage["device"] = "ffffffffffffffffffff" + devID
    dataStorage["location"] = {"type":"Point","coordinates":[-122.2579268, 37.8749026]}
    dataStorage["time"] = datetime.datetime.utcnow().isoformat() + 'Z'
    dataStorage["pm2_5"] = {"value":pm,"raw":pm,"estimatedAccuracy":10}
    dataStorage["recId"] = devID + "_" + datetime.datetime.utcnow().isoformat() + 'Z'
    f = requests.post(baseurl, json=dataStorage)
    content = f.json()
    print(content)
    print(f.status_code)
    time.sleep(1)

