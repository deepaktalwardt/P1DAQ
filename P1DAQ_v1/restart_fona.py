## Restart fona ##
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

fona_key = 22
GPIO.setup(fona_key, GPIO.OUT)

GPIO.output(fona_key, 0)
time.sleep(2)

# print('Turning on GPRS')
# GPRS_on()