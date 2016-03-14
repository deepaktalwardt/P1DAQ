#################################
# Command Client to MQTT Broker #
#################################
import paho.mqtt.client as paho
import os
import json
import csv
import datetime
import sys
import time

ORG_ID          =   "CLMTCO"
DEVICE_TYPE     =   "P1"
dev_id = "c1c8"
topic_sub = 'iot/SSRIOT/P1/#'
topic_pub = "iot/SSRIOT/P1/" + dev_id
tn = "d-" + ORG_ID + "-" + DEVICE_TYPE + "-" + dev_id
sn = 100
cid = 3
cmd = 'set_clock' #

tz_test = ['+04:00',
		   '+08:00',
		   '-03:00',
		   '-08:00',
		   '-10:00']

def on_publish(client, userdata, mid):
	print("Published Command: "+str(mid))

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

    to_send['c'] = c
    to_send['ts'] = ts
    return json.dumps(to_send)

client = paho.Client()
client.on_publish = on_publish
client.on_message = on_message
client.connect('broker.hivemq.com', port=1883)
client.loop_start()

client.subscribe(topic_sub, qos=1)

for tz in tz_test:
	command = build_set_clock_command(tn, sn, cid, cmd, tz)
	(rc, mid) = client.publish(topic_pub, command, qos=1)
	time.sleep(6)