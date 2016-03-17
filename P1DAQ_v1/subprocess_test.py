from subprocess import call
import time
import os

while True:
	call('poff fona')
	time.sleep(12)
	call('pon fona')
	time.sleep(12)