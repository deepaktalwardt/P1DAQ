import time
from THpythonLib import *

while True:
  # htu_reset()
   temperature = read_temperature()
   time.sleep(0.5)
   humidity = read_humidity()
   print(temperature, humidity)
   time.sleep(0.5)
