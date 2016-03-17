from subprocess import call
import time

while True:
	call('sudo poff fona')
	time.sleep(12)
	call('sudo pon fona')
	time.sleep(12)