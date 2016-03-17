from __future__ import print_function
import logging
import os
import time
from GsmModem.modem import GsmModem

def GPRS_off():
    os.system('poff fona')
    #print('Turning Cellular Data OFF')
    time.sleep(3)

def GPRS_on():
    os.system('pon fona')
    #print('Turning Cellular Data ON...')
    time.sleep(5)

def handleSms(sms):
    print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    #reply_text = update_user_pass(sms.text)
    cred = sms.text.split(',')
    print(cred[0])
    print(cred[1])
    #print('Replying to SMS...')
    #sms.reply(reply_text[1])
    sms.reply(u'SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
    #print('SMS sent.\n')
    return

def listen_for_sms():
    #print('Initializing modem...')
    # Uncomment the following line to see what the modem is doing:
    # logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.smsTextMode = False 
    modem.connect()
    print('Waiting for SMS message...')    
    try:    
        modem.rxThread.join(60) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        print('Closing modem')
        modem.close();
        return 
    # if UP_RECEIVED:
    #     print('Closing modem')
    #     time.sleep(2)
    #     modem.close()
    #     return

GPRS_off()
listen_for_sms()
GPRS_on()

