## Restart fona ##
import RPi.GPIO as GPIO
import time
import os
import socket
import atexit

connected = False
REMOTE_SERVER = "www.ping.com"

GPIO.setmode(GPIO.BCM)
fona_key = 22
fona_ps = 12
GPIO.setup(fona_key, GPIO.OUT)
GPIO.setup(fona_ps, GPIO.IN)

atexit.register(GPIO.cleanup)

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
	GPIO.output(fona_key, 1)

def powered():
	return GPIO.input(fona_ps)

if powered():
	print('Restarting')
	toggle_fona()
	toggle_fona()
else:
	print('Turning on')
	toggle_fona()

time.sleep(5)