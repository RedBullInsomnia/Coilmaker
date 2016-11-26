#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import threading
import logging
import sys
import traceback
import serial

class LockSerial():
    """Un verrou qui sécurise le SPI."""
    
    def __init__(self):
        self.name = 'SERIAL - Lock'
        self.lock = threading.Lock()
        self.ser = serial.Serial(port='/dev/ttyAMA0',
                        baudrate = 57600, #9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout = 1)

        self.l = logging.getLogger(self.__class__.__name__)
        
    def readWrite(self,tab):
        self.lock.acquire(True)
        self.ser.write(bytearray(tab))
        self.ser.flush()
        rep = self.ser.read(9)
        ans = []
        for i in rep:
	    ans.append(ord(i))
	self.lock.release()
        return ans
    
    def write(self,tab):
        self.lock.acquire(True)
        self.ser.write(bytearray(tab))
        self.ser.flush()
	self.lock.release()
    
    def close(self):
        self.ser.close()
