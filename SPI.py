#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import spidev
import time
import RPi.GPIO as GPIO

spi = spidev.SpiDev()
spi.open(0,1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT,initial = GPIO.HIGH)
GPIO.setup(17,GPIO.OUT,initial = GPIO.HIGH)
try :
        while True :
            resp = spi.xfer2([0xAA])
            spi.writebytes([0x05])
            resp2 = spi.readbytes(1)

            time.sleep(0.1)
            print resp
            print '\n'
            print resp2
        #end while
except KeyboardInterrupt :
    spi.close()

#end try
