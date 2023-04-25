#!/usr/bin/env python3

"""
Demo: Send Simple SMS Demo
Simple demo to send sms via gsmmodem package
"""
from __future__ import print_function

import logging

from gsmmodem.modem import GsmModem, SentSms

# PORT = 'COM5' # ON WINDOWS, Port is from COM1 to COM9 ,
# We can check using the 'mode' command in cmd
PORT = '/dev/ttyUSB2'
BAUDRATE = 115200
# SMS_TEXT = 'test from python script'
# SMS_DESTINATION = 'PHONENR'
PIN = 1415  # SIM card PIN (if any)


def send(destination, code):
    print('Initializing modem...')
    modem = GsmModem(PORT, BAUDRATE)
    modem.connect(PIN)
    modem.waitForNetworkCoverage(10)
    print("connected")
    print('Sending SMS to: {0}'.format(destination))
    # response = modem.sendSms(destination, code, True)
    # if type(response) == SentSms:
        # print('SMS Delivered.')
    # else:
        # print('SMS Could not be sent')

    modem.close()


# if __name__ == '__main__':
#     main()