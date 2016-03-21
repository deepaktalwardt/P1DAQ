import os
import time
import json
import sys
from subprocess import *

# output_of_sms = subprocess.check_output(['python', 'sms_test.py'])
# print(output_of_sms)
updated = False

output = []

def GPRS_on():
    os.system('pon fona')
    # print('Turning Cellular Data ON...')
    time.sleep(5)

proc = Popen(['python', 'sms_handler.py'], stdout=PIPE)
for line in proc.stdout:
	output.append(line)
	# print(str(line))

if int(output[-3]) == 1:
	updated = True

if updated:
	username = output[-2]
	password = output[-1]
	print('Received: ')
	print(username)
	print(password)
	print(output)
else:
	print('Did not update...Restarting')
	print(output)
	os.system('python3 cred_read.py')

GPRS_on()
