####################
# Simple MQTT Publish test #
####################
import paho.mqtt.client as paho
import time
import json
import random

def on_publish(client, userdata, mid):
	#print("mid: "+str(mid))
	print(" ")

def on_message(client, userdata, msg):
	print(str(msg.payload))

client = paho.Client()
client.on_publish = on_publish
client.on_message = on_message
client.connect('119.81.84.237',port=1883)
client.loop_start()

client.subscribe("clarity/pm25", qos=1)
#client.loop_forever()

while True:
	pm25 = random.randint(1, 500)
	print("Uploaded: " + str(pm25))
	(rc, mid) = client.publish("clarity/pm25", str(pm25), qos=1)
	time.sleep(2)
