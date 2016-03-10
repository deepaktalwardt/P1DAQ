#######################################
# Convert to MQTT JSON for IBM Server #
#######################################
import json
import paho.mqtt.client as paho
import time
import datetime

ORG_ID 			= 	"CLMTCO" 					# Provided by IBM later
DEVICE_TYPE 	= 	"P1"
USERNAME 		= 	"sensoriot_xx"				# Provided by IBM later
PASSWORD 		= 	"sensoriot*xx360"			# Provided by IBM later
TOPIC_UP		=	"iot/SSRIOT/" + DEVICE_TYPE # Check with IBM
TOPIC_DOWN		=	"iot/SSRIOT/" + DEVICE_TYPE + "/" + DEVICE_ID
DEVICE_IDS 		=	["c1c3", "c1c8", "c1c9", "c1b2", "c1b4"]
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

def pub_MQTT_JSON(data):
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
		int_temp = data.get("In Temp (deg C)") # Change later to function call
		out_temp = data.get("Out Temp (deg C)") # Change later to function call
		out_humi = data.get("Relative Humidity (%)") # Change later to function call
		time_now = data.get("Time (UT)")
		air_flow = 1000 # Not sure if we need to change this
		sampling_time = 3 # May need to change later
		sample_number = SAMPLE_NUMBERS[DEVICE_ID]

		# Generate Sub JSONs
		psd["unit"] = "cpcm3" # Counts per cm3
		psd["pm25num"] = data.get(DEVICE_ID + "_nc") #data.get(DEVICE_ID + "_nc")

		mc["unit"] = "ugpm3" # ug per m3
		mc["pm25conc"] = data.get(DEVICE_ID + "_mc") #data.get(DEVICE_ID + "_mc")

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

		# Publish JSON to MQTT
		(rc, mid) = client.publish(TOPIC + "/" + DEVICE_ID, json.dumps(to_send), qos=1)