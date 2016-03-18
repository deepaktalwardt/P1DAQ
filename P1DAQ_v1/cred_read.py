import os
import time
import json
from subprocess import *

# output_of_sms = subprocess.check_output(['python', 'sms_test.py'])
# print(output_of_sms)

proc = Popen(['python', 'sms_test.py'], stdout=PIPE)
for line in proc.stdout:
	print(line)

parsed_json = json.loads(str(line)[2:-1])
print(str(parsed_json[0]), str(parsed_json[1]))