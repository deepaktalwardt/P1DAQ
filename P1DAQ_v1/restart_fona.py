## Restart fona ##
import RPi.GPIO as GPIO
import time
import os
import socket
import atexit

connected = 0
REMOTE_SERVER = "www.ping.com"
restart_file_name = "/mnt/Clarity/restart_counts.txt"

GPIO.setmode(GPIO.BCM)
fona_key = 22
fona_ps = 12
GPIO.setup(fona_key, GPIO.OUT)
GPIO.setup(fona_ps, GPIO.IN)

atexit.register(GPIO.cleanup)

def increment_restart_counter():
	with open(restart_file_name, "r") as file_to_read:
		restart_counts = int(file_to_read.read())

		restart_counts += 1
		print("Restart Counts: " + str(restart_counts))

	with open(restart_file_name, "w") as file_to_write:
		file_to_write.write(str(restart_counts))

# def GPRS_off():
#     os.system('poff fona')
#     time.sleep(3)

# def GPRS_on():
#     os.system('pon fona')
#     time.sleep(5)

# def is_connected():
# 	global connected
# 	try:
# 		host = socket.gethostbyname(REMOTE_SERVER)
# 		s = socket.create_connection((host, 80), 2)
# 		print('Connected!')
# 		connected = True
# 		return True
# 	except:
# 		print('Not Connected')
# 		connected = False
# 		pass
# 	return False

def toggle_fona():
	print('Toggling')
	GPIO.output(fona_key, 0)
	time.sleep(2)
	GPIO.output(fona_key, 1)
	time.sleep(2)

def powered():
	return GPIO.input(fona_ps)

def restart():
	if powered():
		print('Restarting')
		toggle_fona()
		toggle_fona()
	else:
		print('Turning on')
		toggle_fona()

def main():
	fona_counts = 0
	restart()
	if powered():
		print('Powered!')
		return
	else:
		while not powered() or fona_counts < 2:
			print('Not powered, retrying')
			fona_counts += 1
			restart()

increment_restart_counter()
main()
time.sleep(10)
# GPIO.cleanup()