#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import DEFINE as df
from moteur import Moteur


class Position(Moteur):
    def __init__(self, ser, mem, run_event, newCoil_event):
        """Permet le déplacement."""
        Moteur.__init__(self, run_event, newCoil_event, name='Deplacement')
        self.ser = ser
        self.mem = mem
        self.startPos = 0
        self.stopPos = 0
        self.currentPos = 0
        self.speed = 0
        self.enPause = False
        self.direction = 0
        self.couche = 0
        #   0 = non défini
        #   1 = retour
        #   2 = aller

    def configure(self):
        msg = [df.mot_1, df.GAP, 1, 0, 0, 0, 0, 0]
        resp = self.ser.readWrite(msg)
        print("respyyy: ", resp)
        self.startPos = self.bytesToInt(resp[4:8])
        self.stopPos = self.computeStopPos(self.startPos)
        print("stopposyyy: ", self.stopPos)
        time.sleep(0.1)

        #  Moving speed is 1,2 * DFIL, by default
        movingSpeed = self.computeMovingSpeed()
        msg = [df.mot_1, df.SAP, 4, 0] + self.intToBytes(movingSpeed)
        self.ser.write(msg)
        time.sleep(0.1)
        self.l.info("Moteur de translation configuré")
        self.direction = 2
        self.configurate = True

    def computeStopPos(self, startPos):
        coil_length = float(str(
            self.mem.core.dicoBobine[df.LBOBINE]).replace(',', '.'))
        return int(startPos + coil_length * 1000 * 63.952)

    def computeMovingSpeed(self):
        return int(0.2 * float(str(self.mem.core.dicoBobine[df.DFIL]).
                   replace(',', '.')) * 2.047)

    def preBoucle(self):
        mess = [df.mot_1, df.MVP, 0x00, 0x00] + self.intToBytes(self.stopPos)
        print("messy:", mess)
        print("Start pos: {}".format(self.intToBytes(self.startPos)))
        print("Stop pos: {}".format(self.intToBytes(self.stopPos)))
        self.ser.write(mess)
        self.couche = 1
        time.sleep(0.5)

    def boucle(self):
        if self.enPause:
            self.enPause = False
            if self.direction == 1:
                msg = [df.mot_1, df.MVP, 0, 0] + self.intToBytes(self.startPos)
                self.ser.write(msg)
            else:
                msg = [df.mot_1, df.MVP, 0, 0] + self.intToBytes(self.stopPos)
                self.ser.write(msg)
            time.sleep(0.5)

        time.sleep(0.2)
        mess = [df.mot_1, df.GAP, 3, 0, 0, 0, 0, 0]
        resp = self.ser.readWrite(mess)
        if resp[0:9] == [0, 2, 1, 100, 6, 0, 0, 0, 0]:
            mess = [df.mot_1, df.GAP, 1, 0, 0, 0, 0, 0]
            resp = self.ser.readWrite(mess)
            print("resp:", resp)
            if 1 == self.direction:
                self.direction = 2
                mess = [df.mot_1, df.MVP, 0, 0] + self.intToBytes(self.stopPos)
                self.ser.write(mess)
                self.couche += 1
            else:
                self.direction = 1
                mess = [df.mot_1, df.MVP, 0, 0] + self.intToBytes(self.startPos)
                self.ser.write(mess)
                self.couche += 1
        time.sleep(0.1)

    def pause(self):
        if not self.enPause:
            msg = [df.mot_1, df.MST, 0, 0, 0, 0, 0, 0]
            self.ser.write(msg)
        self.enPause = True
        time.sleep(0.1)

    def postBoucle(self):
        msg = [df.mot_1, df.MST, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.ser.write(msg)
        time.sleep(0.1)
        mess = [df.mot_1, df.SAP, 4, 0] + self.intToBytes(1000)
        self.ser.write(mess)
        self.direction = 0
        self.configurate = False

    def intToBytes(self, integer):
        """Converts an unsigned integer into an array of 4 bytes, in a big-endian
           fashion. Used to send the number of µsteps to the servos.
            arguments :
                - integer : an unsigned integer

            returns [byte[0], byte[1], byte[2], byte[3]]
        """
        _bytes = [0, 0, 0, 0]

        _bytes[0] = integer / (256**3)
        integer = integer % (256**3)
        _bytes[1] = integer / (256**2)
        integer = integer % (256**2)
        _bytes[2] = integer / 256
        integer = integer % 256
        _bytes[3] = integer

        return _bytes

    def bytesToInt(self, bytes):
        """Converts an array of 4 bytes into an integer, in a big-endian
           fashion.
            arguments :
                - bytes : an array of 4 bytes

            returns integer
        """
        ans = bytes[0]*256**3 + bytes[1]*256**2 + bytes[2]*256 + bytes[3]

        return ans
