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

ORG_ID          =   	"CLMTCO"
DEVICE_TYPE     =   	"P1"
BOX 			= 		"P1DAQ1"
#dev_ids 		=		["0001", "0024", "000c", "0027", "0031"]
dev_ids = ["0012", "0014", "0016", "0020", "000f"]
PUBLIC_BROKER   =   	"broker.hivemq.com"
IBM_BROKER      =   	"119.81.84.237"
BROKER          =   	IBM_BROKER
topic_sub 		= 		"iot/SSRIOT/P1/"
topic_pub		= 		"iot/SSRIOT/P1/"
t_n 			= 		BOX + "-" + DEVICE_TYPE + "-"

tz_test = ['+04:00',
		   '+08:00',
		   '-03:00',
		   '-08:00',
		   '-10:00']

st_test = [10, 5, 8, 12, 6]

dev_name_test = ['heyo', 'yuhu', 'yayy', 'clay', 'peep']

def on_publish(client, userdata, mid):
	print("Published Command: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
	print(str(msg.payload))

client = paho.Client()
client.on_publish = on_publish
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(BROKER, port=1883)
client.loop_start()

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

# for st in st_test:
# 	command = build_command(tn, dev_id[0], 1, 'set_st', st)
# 	(rc, mid) = client.publish(topic_pub, command, qos=1)
# 	sleep_time = 2.1*st*2.5
# 	print('Sleeping for: ' + str(sleep_time) + 'sec')
# 	time.sleep(sleep_time)
# 	if random.randint(0,10) > 3:
# 		command = build_set_clock_command(tn, sn, 3, 'set_clock', tz_test[random.randint(0,4)])
# 		print('Time command sent: ')
# 		(rc, mid) = client.publish(topic_pub, command, qos=1)
# 		time.sleep(1)

def test_set_st():
	i = 0
	for dev_id in dev_ids:
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 1, 'set_st', st_test[i])
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		i += 1
		time.sleep(3)
	print('Testing failure cases')
	print('Wrong CID')
	i = 0
	for dev_id in dev_ids:
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 2341, 'set_st', st_test[i])
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		i += 1
		time.sleep(3)
	print('Argument as a string')
	i = 0
	for dev_id in dev_ids:
		tn = tn + dev_id
		sn = dev_id
		command = build_command(tn, sn, 1, 'set_st', 'dsf')
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		i += 1
		time.sleep(3)

def test_get_st():
	for dev_id in dev_ids:
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 2, 'get_st', ' ')
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(3)
	print('Testing failure cases')
	print('Wrong CID')
	for dev_id in dev_ids:
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 2341, 'get_st', ' ')
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(3)

def test_tz():
	for tz in tz_test:
		tn = t_n + dev_id
		sn = dev_id
		command = build_set_clock_command(tn, sn, 3, 'set_clock', tz)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(8)
	print('Testing failure cases')
	print('Wrong CID')
	for tz in tz_test:
		tn = t_n + dev_id
		sn = dev_id
		command = build_set_clock_command(tn, sn, 4245, 'set_clock', tz)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(8)
	print('Unsupported TZ')
	tz_mock = ['-24:53','2452:325', '453:45']
	for tz in tz_mock:
		tn = t_n + dev_id
		sn = dev_id
		command = build_set_clock_command(tn, sn, 3, 'set_clock', tz)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(8)

def test_set_dev_name():
	for i in range(0,5):
		name = dev_name_test[i]
		dev_id = dev_ids[i]
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 4, 'set_dev_name', name)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(1)
	print('Resetting...')
	for i in range(0,5):
		name = dev_ids[i]
		dev_id = dev_ids[i]
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 4, 'set_dev_name', name)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(1)
	print('Testing failure cases')
	print('Wrong CID')
	for i in range(0,5):
		name = dev_name_test[i]
		dev_id = dev_ids[i]
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 43, 'set_dev_name', name)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(1)
	print('Name not a string')
	for i in range(0,5):
		name = dev_name_test[i]
		dev_id = dev_ids[i]
		tn = t_n + dev_id
		sn = dev_id
		command = build_command(tn, sn, 4, 'set_dev_name', 524523)
		(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
		time.sleep(1)

def test_unrec_cmd():
	command = build_command(tn, sn, 4, 'set_dev', '431f')
	(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
	time.sleep(1)

	command = build_command(tn, sn, 4, 'set_blah', 12)
	(rc, mid) = client.publish(topic_pub+dev_id, command, qos=1)
	time.sleep(1)

test_set_st()
#test_get_st()