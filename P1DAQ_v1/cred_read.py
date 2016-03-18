import os
import time
import json
import subprocess

output_of_sms = subprocess.check_output(['python', 'sms_test.py'])
print(output_of_sms)