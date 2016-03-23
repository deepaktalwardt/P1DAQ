import paho.mqtt.client as paho
import os
import json
import csv
import datetime
import sys

DEVICE_TYPE     =   "P1"
TOPIC           =   "iot/SSRIOT/" + DEVICE_TYPE
COUNTER = 0
dev_ids = ["0001", "0024", "0020", "0027", "000c"]
fieldnames = [dev_ids[0] + "_mc", dev_ids[0] + "_nc", 
			  dev_ids[1] + "_mc", dev_ids[1] + "_nc",
			  dev_ids[2] + "_mc", dev_ids[2] + "_nc",
			  dev_ids[3] + "_mc", dev_ids[3] + "_nc",
			  dev_ids[4] + "_mc", dev_ids[4] + "_nc",
			  "In Temp (deg C)", "Out Temp (deg C)",
			  "Relative Humidity (%)",
			  "Time (UT)"]

folder_name = "/media/pi/Clarity/MQTTData/"
#folder_name = "C:/Users/Deepak/Dropbox (Clarity Movement)/Hardware R&D/P1 sensor/Custom Projects/RPi2/P1DAQ/MQTTtesting/testMQTT/"
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
	print(str(msg.payload)[2:-1])
	jmsg = json.loads(str(msg.payload)[2:-1])
	tn = jmsg.get('d').get('tn')
	dev_id = tn[-4:]
	num_conc = jmsg.get('d').get('psd').get('pm25num')
	mass_conc = jmsg.get('d').get('mc').get('pm25conc')
	int_temp = jmsg.get('d').get('it')
	out_temp = jmsg.get('d').get('ot')
	out_humi = jmsg.get('d').get('oh')
	time = jmsg.get('ts')
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

client = paho.Client(client_id = "p1", clean_session = True)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
for dev_id in dev_ids:
    client.subscribe(TOPIC, qos=1)
 
client.loop_forever()
