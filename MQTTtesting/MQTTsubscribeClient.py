import paho.mqtt.client as paho
import os
import json
import csv
import datetime
import sys

DEVICE_TYPE     =   "P1"
TOPIC           =   "iot/SSRIOT/" + DEVICE_TYPE + "/#"
COUNTER = 0
dev_ids = ["c1c3", "c1c8", "c1c9", "c1b2", "c1b4"]
fieldnames = [dev_ids[0] + "_mc", dev_ids[0] + "_nc", 
			  dev_ids[1] + "_mc", dev_ids[1] + "_nc",
			  dev_ids[2] + "_mc", dev_ids[2] + "_nc",
			  dev_ids[3] + "_mc", dev_ids[3] + "_nc",
			  dev_ids[4] + "_mc", dev_ids[4] + "_nc",
			  "In Temp (deg C)", "Out Temp (deg C)",
			  "Relative Humidity (%)",
			  "Time (UT)"]

folder_name = "/media/pi/Clarity/MQTTData/"
num_file = len([f for f in os.listdir(folder_name)]) + 1
file_name = folder_name + "MQTTFile" + str(num_file) + ".csv"

dict_to_write = dict.fromkeys(fieldnames)

with open(file_name, "a") as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()

def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))
 
def on_message(client, userdata, msg):
	global COUNTER
	global dict_to_write
	print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
	jmsg = json.loads(msg.payload)
	tn = jmsg['tn']
	dev_id = tn[-4:]
	num_conc = jmsg['d']['psd']['pm25num']
	mass_conc = jmsg['d']['mc']['pm25conc']
	int_temp = jmsg['d']['it']
	out_temp = jmsg['d']['ot']
	out_humi = jmsg['d']['oh']
	time = jmsg['ts']
	dict_to_write[dev_id + '_mc'] = mass_conc
	dict_to_write[dev_id + '_nc'] = num_conc
	dict_to_write['Time (UT)'] = time
	dict_to_write['In Temp (deg C)'] = int_temp
	dict_to_write['Out Temp (deg C)'] = out_temp
	dict_to_write['Relative Humidity (%)'] = out_humi
	COUNTER += 1
	if COUNTER % 5 == 0:
		print("Saving now")
		with open(file_name, "a") as file_to_update:
			updater = csv.DictWriter(file_to_update, fieldnames = fieldnames)
			updater.writerow(dict_to_write)

client = paho.Client(client_id = "p1", clean_session = False)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe(TOPIC, qos=1)
 
client.loop_forever()