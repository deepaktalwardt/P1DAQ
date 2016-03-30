import paho.mqtt.client as paho
import os
import json
import csv
import datetime
import sys
from queue import Queue
from threading import Thread

###############################################################
# File Saving stuff
DEVICE_TYPE = "P1"
TOPIC = "iot/SSRIOT/" + DEVICE_TYPE + "/#"
dev_ids = ["0012", "0014", "002c", "0020", "000f", "0001", "0024", "000c", "0027", "0031"]
folder_name = "C:/Users/Deepak/Dropbox (Clarity Movement)/Hardware R&D/P1 sensor/Custom Projects/RPi2/P1DAQ/MQTTtesting/IBM_test/"

fieldnames = ['mc', 'nc', 'it', 'ot', 'oh', 'time']
file_names = {}
for dev_id in dev_ids:
	num_file = len([f for f in os.listdir(folder_name+dev_id+"/")]) + 1
	file_names[dev_id] = folder_name+dev_id+"/" + dev_id + "_" + str(num_file) + ".csv"

for dev_id in dev_ids:
	with open(file_names[dev_id], "a") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()

def save_to_file(q):
	while True:
		dict_to_write = {}
		msg = q.get()
		jmsg = json.loads(str(msg)[2:-1])

		tn = jmsg.get('d').get('tn')
		dev_id = tn[-4:]
		print("Working on: " + dev_id)
		num_conc = jmsg.get('d').get('psd').get('pm25num')
		mass_conc = jmsg.get('d').get('mc').get('pm25conc')

		int_temp = jmsg.get('d').get('it')
		out_temp = jmsg.get('d').get('ot')
		out_humi = jmsg.get('d').get('oh')
		time = jmsg.get('ts')

		dict_to_write['mc'] = mass_conc
		dict_to_write['nc'] = num_conc
		dict_to_write['it'] = int_temp
		dict_to_write['ot'] = out_temp
		dict_to_write['oh'] = out_humi
		dict_to_write['time'] = time

		with open(file_names[dev_id], "a") as file_to_update:
			updater = csv.DictWriter(file_to_update, fieldnames = fieldnames, lineterminator='\n')
			updater.writerow(dict_to_write)
		q.task_done()

###############################################################
# MQTT stuff
msg_queue = Queue(maxsize=0)
num_threads = 2

for i in range(num_threads):
	worker = Thread(target=save_to_file, args=(msg_queue,))
	worker.setDaemon(True)
	worker.start()

def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
	print('Message received from:'+msg.topic)
	msg_queue.put(msg.payload)

client = paho.Client(client_id = "p1client", clean_session = True)
client.on_subscribe = on_subscribe
client.on_message = on_message
#client.connect("broker.hivemq.com", 1883)
client.connect("119.81.84.237", 1883)
# for dev_id in dev_ids:
#     client.subscribe(TOPIC, qos=1)
client.subscribe(TOPIC,qos=1)

client.loop_forever()
