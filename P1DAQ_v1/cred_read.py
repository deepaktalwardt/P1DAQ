import os
import time
import json
from subprocess import *

# output_of_sms = subprocess.check_output(['python', 'sms_test.py'])
# print(output_of_sms)
updated = False

output = []

def GPRS_on():
    os.system('pon fona')
    # print('Turning Cellular Data ON...')
    time.sleep(5)

proc = Popen(['python', 'sms_test.py'], stdout=PIPE)
for line in proc.stdout:
	output.append(line)
	# print(str(line))

if output[-3] == True:
	updated = True

if updated:
	username = output[-2]
	password = output[-1]
	print('Received: ')
	print(username)
	print(password)
else:
	print('Did not update')

print(output)
GPRS_on()
