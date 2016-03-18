from __future__ import print_function
import logging
import os
import time
import json
from gsmmodem.modem import GsmModem

PORT = '/dev/ttyAMA0'
BAUDRATE = 115200
TIMEOUT = 60
cred = ''
DESTINATION = '+15592734835'
correct_format = 0
modem = ''

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
    cred = sms.text
    sms_reply = check_sms(sms.text)
    modem.sendSms(sms.number, sms_reply[1])
    print('SMS sent.\n')

def check_sms(sms_text):
    global correct_format
    cred_split = str(sms_text).split(',')
    to_reply = ['','']
    if len(cred_split) == 2:
        correct_format = 1
        #print("I just checked the length and it's equal to" + str(len(cred_split)))
        to_reply[0] = correct_format
        to_reply[1] = "SUCCESS | Username: " + cred_split[0].strip() + " Password: " + cred_split[1].strip()
        print(to_reply)
        return to_reply
    else:
        correct_format = 0
        to_reply[0] = correct_format
        to_reply[1] = 'FAIL | Try again: <USERNAME>,<PASSWORD>'
        print(to_reply)
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
    first_text = u'Waiting for credentials | <USERNAME>,<PASSWORD>'
    sentmsg = modem.sendSms(DESTINATION, first_text)
    print('Waiting for SMS message')    
    try:    
        modem.rxThread.join(TIMEOUT) 
    finally:
        print('Closing modem')
        if correct_format == 1:
            #print("the format is correct and equal to")
            print(correct_format)
            cred_return = cred.split(',')
            print(cred_return[0].strip())
            print(cred_return[1].strip())
        else:
            #print("the format is NOT correct and equal to")
            print(correct_format)
            print('')
            print('')
        modem.close()

GPRS_off()
listen_for_sms()