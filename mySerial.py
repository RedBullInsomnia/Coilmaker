#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import threading
import logging
import serial


class LockSerial():
    """Un verrou qui sécurise le SPI."""

    def __init__(self):
        self.name = 'SERIAL - Lock'
        self.lock = threading.Lock()
        self.ser = serial.Serial(port='/dev/ttyAMA0',
                                 baudrate=57600,  # 9600 by default
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout=1)

        self.l = logging.getLogger(self.__class__.__name__)

    def readWrite(self, bytes_list):
        self.lock.acquire(True)
        self.addChecksum(bytes_list)
        self.ser.write(bytearray(bytes_list))
        self.ser.flush()
        rep = self.ser.read(9)
        ans = []
        for i in rep:
            ans.append(ord(i))

        self.lock.release()

        return ans

    def write(self, bytes_list):
        self.lock.acquire(True)
        self.addChecksum(bytes_list)
        self.ser.write(bytearray(bytes_list))
        self.ser.flush()

        self.lock.release()

    def addChecksum(self, bytes_list):
        """Computes the checksum of a list of bytes and appends it
            arguments:
                - bytes_list

            returns [array8_list checksum]
        """
        checksum = 0
        for elem in bytes_list:
            checksum += elem
        checksum = int(checksum % 256)

        return bytes_list.append(checksum)

    def close(self):
        self.ser.close()
