#!/usr/bin/env python3

from __future__ import print_function

from gsmmodem.modem import GsmModem, SentSms

PORT = "/dev/ttyUSB2"
BAUDRATE = 115200
PIN = 1415  # SIM card PIN (if any)


def send(destination, code):
    print("Initializing modem...")
    modem = GsmModem(PORT, BAUDRATE)
    modem.connect(PIN)
    modem.waitForNetworkCoverage(10)
    print("connected")
    print('Sending SMS to: {0}'.format(destination))
    response = modem.sendSms(destination, code, True)
    if type(response) == SentSms:
        print('SMS Delivered.')
    else:
        print('SMS Could not be sent')

    modem.close()

