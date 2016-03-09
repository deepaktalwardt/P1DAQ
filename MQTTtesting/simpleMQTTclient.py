####################
# Simple MQTT Publish test #
####################
import paho.mqtt.client as paho
import time
import json
import random

def on_publish(client, userdata, mid):
	print("mid: "+str(mid))

client = paho.Client()
client.on_publish = on_publish
client.connect("0.0.0.0", port=1883)
client.loop_start()

while True:
	pm25 = random.randint(1, 500)
	(rc, mid) = client.publish("clarity/pm25", str(pm25), qos=1)
	time.sleep(2)
