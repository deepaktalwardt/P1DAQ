#import urllib3
import json
import datetime
from requests import requests
import time

baseurl = "https://api.clarity.io/v2/measurements"
devID = "be83"

tic = time.clock()
dataStorage = {}
dataStorage["device"] = "ffffffffffffffffffff" + devID
dataStorage["location"] = {"type":"Point","coordinates":[-122.2579268, 37.8749026]}
dataStorage["time"] = datetime.datetime.now().isoformat()
dataStorage["pm2_5"] = {"value":500,"raw":34,"estimatedAccuracy":10}
#dataStorage["recId"] = devID + "_" + datetime.datetime.now().isoformat()
#print(dataStorage)
json_data = json.dumps(dataStorage)
#json_data = json.JSONEncoder().encode(data)
#print(json_data)
for i in range(0,6):
    dataStorage["recId"] = devID + "_" + datetime.datetime.now().isoformat()
    #print(dataStorage)
    f = requests.post(baseurl, json=dataStorage)
    content = f.json()
    print(content)
    time.sleep(0.01)
    #print(f.content)
    #f.headers
    #print(f.status_code)
toc = time.clock()
#print(toc-tic)
