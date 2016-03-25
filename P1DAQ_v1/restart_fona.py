## Restart fona ##
import RPi.GPIO as GPIO
import time
import os

def GPRS_off():
    os.system('poff fona')
    time.sleep(3)

def GPRS_on():
    os.system('pon fona')
    time.sleep(5)

GPRS_off()
GPIO.setmode(GPIO.BCM)

fona_key = 22
GPIO.setup(fona_key, GPIO.OUT)

GPIO.output(fona_key, 0)
time.sleep(2)

GPIO.cleanup()
time.sleep(10)
# GPRS_on()




