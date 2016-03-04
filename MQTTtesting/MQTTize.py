#######################################
# Convert to MQTT JSON for IBM Server #
#######################################
import json
import paho.mqtt.client as paho
import time
import random
import datetime

ORG_ID 			= 	"CLMTCO" 					# Provided by IBM later
DEVICE_TYPE 	= 	"P1"
USERNAME 		= 	"sensoriot_xx"				# Provided by IBM later
PASSWORD 		= 	"sensoriot*xx360"			# Provided by IBM later
TOPIC 			=	"iot/SSRIOT/" + DEVICE_TYPE # Check with IBM
DEVICE_IDS 		=	["c1b6", "c1b1", "c1b7", "c1b3", "c1b5"]
SAMPLE_NUMBERS	=	dict.fromkeys(DEVICE_IDS, 0)

def on_publish(client, userdata, mid):
	print("mid: " + str(mid))

def on_connect(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))

client = paho.Client(client_id = "d-" + ORG_ID + "-" + DEVICE_TYPE)
client.on_publish = on_publish
client.on_connect = on_connect
client.connect("broker.hivemq.com", 1883)
client.loop_start()

def gen_MQTT_JSON(data):
	global SAMPLE_NUMBERS
	for DEVICE_ID in DEVICE_IDS:
		SAMPLE_NUMBERS[DEVICE_ID] = SAMPLE_NUMBERS.get(DEVICE_ID) + 1

		# Initialize all JSONs
		to_send = {}
		d = {}
		psd = {}
		mc = {}

		# Generate variables
		t_n = "d-" + ORG_ID + "-" + DEVICE_TYPE + "-" + DEVICE_ID
		int_temp = random.randint(22, 25) # Change later to function call
		out_temp = random.randint(26, 29) # Change later to function call
		out_humi = random.randint(20, 45) # Change later to function call
		time_now = datetime.datetime.now().isoformat()
		air_flow = 1000 # Not sure if we need to change this
		sampling_time = 3 # May need to change later
		sample_number = SAMPLE_NUMBERS[DEVICE_ID]

		# Generate Sub JSONs
		psd["unit"] = "cpcm3" # Counts per cm3
		psd["pm25num"] = random.randint(1,10) #data.get(DEVICE_ID + "_nc")

		mc["unit"] = "ugpm3" # ug per m3
		mc["pm25conc"] = random.randint(11,20) #data.get(DEVICE_ID + "_mc")

		d["tn"] = t_n
		d["sn"] = sample_number
		d["st"] = sampling_time
		d["psd"] = psd
		d["mc"] = mc
		d["af"] = air_flow
		d["it"] = int_temp
		d["ot"] = out_temp
		d["oh"] = out_humi

		# Generate to_send JSON
		to_send["d"] = d
		to_send["ts"] = time_now
		print(to_send)

		# Publish to the MQTT Broker
		(rc, mid) = client.publish(TOPIC + "/" + DEVICE_ID, json.dumps(to_send), qos=1)
		time.sleep(2)

while True:
	gen_MQTT_JSON({})
	