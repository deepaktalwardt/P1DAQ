import time
import pigpio
import math

pi = pigpio.pi()

# Sensor Address on I2C
addr = 0x40

# I2C bus on Raspberry Pi 2
bus = 1

# Sensor Commands
rdtemp = 0xE3
rdhumi = 0xE5
wtreg = 0xE6
rdreg = 0xE7
reset = 0xFE

def htu_reset():
	handle = pi.i2c_open(bus, addr)
	pi.i2c_write_byte(handle, reset)
	pi.i2c_close(handle)
	time.sleep(0.2)

def read_temperature():
	try:
		handle = pi.i2c_open(bus, addr)
		pi.i2c_write_byte(handle, rdtemp)
		time.sleep(0.055)
		(count, byteArray) = pi.i2c_read_device(handle, 3)
		pi.i2c_close(handle)
		t1 = byteArray[0]
		t2 = byteArray[1]
		temp_reading = (t1*256)+t2
		temp_reading = round(temp_reading,2)
		temperature = ((temp_reading/65536)*175.72)-46.85
		return temperature
	except:
		return -1

def read_humidity():
	try:
		handle = pi.i2c_open(bus, addr)
		pi.i2c_write_byte(handle, rdhumi)
		time.sleep(0.055)
		(count, byteArray) = pi.i2c_read_device(handle, 3)
		pi.i2c_close(handle)
		h1 = byteArray[0]
		h2 = byteArray[1]
		humi_reading = (h1*256)+h2
		humi_reading = round(humi_reading,2)
		uncomp_humidity = ((humi_reading/65536)*125)-6
		temperature = read_temperature()
		humidity = ((25-temperature)*-0.15)+uncomp_humidity
		return humidity
	except:
		return -1