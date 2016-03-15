#################################
# Command Client to MQTT Broker #
#################################
import paho.mqtt.client as paho
import os
import json
import csv
import datetime
import sys
import random
import time

ORG_ID          =   "CLMTCO"
DEVICE_TYPE     =   "P1"
dev_id = "002d"
topic_sub = 'iot/SSRIOT/P1/' + dev_id
topic_pub = "iot/SSRIOT/P1/" + dev_id
tn = "d-" + ORG_ID + "-" + DEVICE_TYPE + "-" + dev_id
#sn = 100
#cid = 3
#cmd = 'set_clock' #

tz_test = ['+04:00',
		   '+08:00',
		   '-03:00',
		   '-08:00',
		   '-10:00']

st_test = [2, 5, 8, 1, 4, 1]

def on_publish(client, userdata, mid):
	print("Published Command: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
	print(str(msg.payload))

def build_set_clock_command(tn, sn, cid, cmd, tz):
    # Initialize all JSONs
    to_send = {}
    c = {}

    # Populate individual JSONs
    c['tn'] = tn
    c['sn'] =  sn
    c['cid'] = cid
    c['cmd'] = cmd

    ts = datetime.datetime.now().isoformat() + tz
    arg = ts

    c['arg'] = arg

    to_send['c'] = c
    to_send['ts'] = ts
    return json.dumps(to_send)

client = paho.Client()
client.on_publish = on_publish
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect('broker.hivemq.com', port=1883)
client.loop_start()

client.subscribe(topic_sub, qos=1)

def build_command(tn, sn, cid, cmd, arg):
	# Initialize all JSONs
    to_send = {}
    c = {}

    # Populate individual JSONs
    c['tn'] = tn
    c['sn'] =  sn
    c['cid'] = cid
    c['cmd'] = cmd

    ts = datetime.datetime.now().isoformat()

    c['arg'] = arg

    to_send['c'] = c
    to_send['ts'] = ts
    return json.dumps(to_send)


for st in st_test:
	command = build_command(tn, 100, 1, 'set_st', st)
	(rc, mid) = client.publish(topic_pub, command, qos=1)
	sleep_time = 2.1*st*2.5
	print('Sleeping for: ' + str(sleep_time) + 'sec')
	time.sleep(sleep_time)
	if random.randint(0,10) > 7:
		command = build_set_clock_command(tn, sn, cid, cmd, random.choice(tz_test.keys()))
		print('Time command sent: ')
		(rc, mid) = client.publish(topic_pub, command, qos=1)
		time.sleep(1)