from __future__ import print_function
import logging
import sys
import os
import time
import json
import csv
from gsmmodem.modem import GsmModem

PORT = '/dev/ttyAMA0'
BAUDRATE = 115200
TIMEOUT = 120
BOX = "P1DAQ-1: "
#BOX = "P1DAQ-2: "
DESTINATION = '13761075696' # change this to default number
USERPASS_FILE = "/media/pi/Clarity/mqtt_info.csv"
correct_format = 0
modem = ''
cred = ''
change_required = 0

def load_mqtt():
    # try:
    with open(USERPASS_FILE, 'r') as file_to_read:
        reader = csv.reader(file_to_read)
        for line in reader:
            latest_number = line
        # split_info = latest_number.split(',')
        b = str(latest_number[0]).strip()
        po = str(latest_number[1]).strip()
        u = str(latest_number[2]).strip()
        p = str(latest_number[3]).strip()
        to_return = [b, po, u, p]
        #to_return = latest_number
        print('MQTT info: ' +  to_return)
        return to_return
    # except:
    #     print('File reading failed')
    #     return ["","","",""]

def write_mqtt(url, prt, us, pw):
    print('Writing: '+ str(url) + ", " + str(prt) + ", " + str(us) + ", " + str(pw))
    try:
        with open(USERPASS_FILE, 'w') as file_to_write:
            updater = csv.writer(file_to_write, delimiter=',')
            updater.writerow([url, prt, us, pw])
        print('Priting to file worked')
    except:
        pass

def GPRS_off():
    os.system('poff fona')
    time.sleep(3)

def GPRS_on():
    os.system('pon fona')
    time.sleep(5)

def handleSms(sms):
    global cred
    global correct_format
    print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    print(sms.number)
    if valid_sender(sms):
        cred = sms.text
        sms_reply = check_sms(sms.text)
        #write_dest(str(sms.number).strip())
        modem.sendSms(sms.number, sms_reply[1])
        print('SMS sent.\n')
    else:
        print('SMS not sent')

def valid_sender(rec_sms):
    text = rec_sms.text
    try:
        split_text = str(text).split(',')
        if split_text[0].strip() == 'cmcibm':
            return True
        else:
            return False
    except:
        return False

def check_sms(sms_text):
    global correct_format
    global change_required
    cred_split = str(sms_text).split(',')
    to_reply = ['','']
    extra_message = ". Trying... will request again in case of failure"
    if len(cred_split) == 5:
        correct_format = 1
        change_required = 0
        #broker = cred_split[1]
        #broker_port = cred_split[2]
        to_reply[0] = correct_format
        to_reply[1] = BOX+"SUCCESS | Broker: " + cred_split[1].strip() + ", Port: " + cred_split[2].strip() + ", Username: " + cred_split[3].strip() + ", Password: " + cred_split[4].strip() + extra_message
        write_mqtt(cred_split[1].strip(), cred_split[2].strip(), cred_split[3].strip(), cred_split[4].strip())
        return to_reply
    else:
        correct_format = 0
        to_reply[0] = correct_format
        to_reply[1] = BOX+'FAIL | Try again: cmcibm,<BROKER>,<PORT>,<USERNAME>,<PASSWORD>'
        return to_reply

def listen_for_sms():
    global modem
    global correct_format
    # print('Initializing modem...')
    # Uncomment the following line to see what the modem is doing:
    # logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.smsTextMode = False 
    modem.connect()
    first_text = BOX+' Restart: Waiting for credentials | cmcibm,<BROKER>,<PORT>,<USERNAME>,<PASSWORD>'
    #load_dest()
    sentmsg = modem.sendSms(DESTINATION, first_text)
    print('Waiting for SMS message')    
    try:
        modem.rxThread.join(TIMEOUT) 
    finally:
        print('Closing modem')
        if correct_format == 1:
            #print("the format is correct and equal to")
            to_print = load_mqtt()
            print(change_required)
            print(correct_format)
            print(to_print[0])
            print(to_print[1])
            print(to_print[2])
            print(to_print[3])
        else:
            #print("the format is NOT correct and equal to")
            print(change_required)
            print(correct_format)
            print('')
            print('')
            print('')
            print('')
        modem.close()

change_required = sys.argv[1]
#GPRS_off()
listen_for_sms()