from __future__ import print_function
import logging
import os
import time
import json
from gsmmodem.modem import GsmModem

PORT = '/dev/ttyAMA0'
BAUDRATE = 115200
cred = ''
DESTINATION = '+15592734835'
correct_format = False

def GPRS_off():
    os.system('poff fona')
    # print('Turning Cellular Data OFF')
    time.sleep(3)

def GPRS_on():
    os.system('pon fona')
    # print('Turning Cellular Data ON...')
    time.sleep(5)

def handleSms(sms):
    global cred
    print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    cred = sms.text
    sms_reply = check_sms(sms.text)
    # cred_json['USERNAME'] = cred[0]
    # cred_json['PASSWORD'] = cred[1]
    #return json.dumps(cred_json)
    #print(cred[0])
    #print(cred[1])
    # print('Replying to SMS...')
    # sms.reply(reply_text[1])
    sms.reply(sms_reply[1])
    #print('SMS sent.\n')

def check_sms(sms_text):
    global correct_format
    cred_split = str(sms_text).split(',')
    to_reply = ['','']
    print('Len: ' + str(len(cred_split)))
    if len(cred_split) == 2:
        correct_format = True
        to_reply[0] = correct_format
        to_reply[1] = "SUCCESS | Username: " + cred_split[0] + " Password: " + cred_split[1]
        print(to_reply)
        return to_reply
    else:
        correct_format = False
        to_reply[0] = correct_format
        to_reply[1] = 'FAIL | Try again: <USERNAME>,<PASSWORD>'
        print(to_reply)
        return to_reply


def listen_for_sms():
    # print('Initializing modem...')
    # Uncomment the following line to see what the modem is doing:
    # logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.smsTextMode = False 
    modem.connect()
    first_text = u'Waiting for Username and Password...'
    sentmsg = modem.sendSms(DESTINATION, first_text)
    print('Waiting for SMS message...')    
    try:    
        modem.rxThread.join(80) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        print('Closing modem')
        if correct_format:
            print(correct_format)
            cred_return = cred.split(',')
            print(cred_return[0][2:-3])
            print(cred_return[1][2:-3])
        else:
            print(correct_format)
            print(' ')
            print(' ')
        modem.close()
    # if UP_RECEIVED:
    #     print('Closing modem')
    #     time.sleep(2)
    #     modem.close()
    #     return

GPRS_off()
listen_for_sms()
#GPRS_on()

