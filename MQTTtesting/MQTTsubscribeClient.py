import paho.mqtt.client as paho

DEVICE_TYPE 	= 	"P1"
TOPIC 			=	"iot/SSRIOT/" + DEVICE_TYPE + "/#"

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
 
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))    
 
client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe(TOPIC, qos=1)
 
client.loop_forever()