import os
import time
import json
from subprocess import *

# output_of_sms = subprocess.check_output(['python', 'sms_test.py'])
# print(output_of_sms)

proc = Popen(['python', 'sms_test.py'], stdout=PIPE)
for line in proc.stdout:
	print(str(line))

parsed_json = json.loads(str(line)[1:-4]+str(line)[-1])
# print(parsed_json.get('USERNAME'))
# print(parsed_json.get('PASSWORD'))
print(parsed_json)