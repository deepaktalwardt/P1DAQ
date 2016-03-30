## Restart fona ##
import RPi.GPIO as GPIO
import time
import os
import socket

connected = False
REMOTE_SERVER = "www.baidu.com"

GPIO.setmode(GPIO.BCM)
fona_key = 22
GPIO.setup(fona_key, GPIO.OUT)

def GPRS_off():
    os.system('poff fona')
    time.sleep(3)

def GPRS_on():
    os.system('pon fona')
    time.sleep(5)

def is_connected():
	global connected
	try:
		host = socket.gethostbyname(REMOTE_SERVER)
		s = socket.create_connection((host, 80), 2)
		print('Connected!')
		connected = True
		return True
	except:
		print('Not Connected')
		connected = False
		pass
	return False

def toggle_fona():
	print('Toggling')
	GPIO.output(fona_key, 0)
	time.sleep(2)

while not is_connected():
	toggle_fona()
	time.sleep(10)
	GPRS_on()

GPIO.cleanup()