from subprocess import call
import time
import os

while True:
	os.system('poff fona')
	print('poff fona')
	#call('poff fona')
	time.sleep(12)
	os.system('pon fona')
	print('pon fona')
	#call('pon fona')
	time.sleep(15)