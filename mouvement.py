#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import DEFINE
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
        mess = [1, 6, 1, 0, 0, 0, 0, 0]
        resp = self.ser.readWrite(mess)
        print("respyyy: ", resp)
        self.startPos = resp[4]*256**3 + resp[5]*256**2 + resp[6]*256 + resp[7]
        self.stopPos = self.computeStopPos(self.startPos)
        print("stopposyyy: ", self.stopPos)
        time.sleep(0.1)

        #  Moving speed is 1,2 * DFIL, by default
        movingSpeed = self.computeMovingSpeed()
	mess = [1, 5, 4, 0] + self.convToBytes(movingSpeed)
        self.ser.write(mess)
        time.sleep(0.1)
        self.l.info("Moteur de translation configuré")
        self.direction = 2
        self.configurate = True

    def computeStopPos(self, startPos):
        coil_length = float(str(
            self.mem.core.dicoBobine[DEFINE.LBOBINE]).replace(',', '.'))
        return int(startPos + coil_length*1000*63.952)

    def computeMovingSpeed(self):
        return int(0.2*float(str(self.mem.core.dicoBobine[DEFINE.DFIL]).
                   replace(',', '.')) * 2.047)

    def preBoucle(self):
        mess = [1, 4, 0, 0] + self.convToBytes(self.stopPos)
        print("messy:", mess)
        print("Start pos: {}".format(self.convToBytes(self.startPos)))
        print("Stop pos: {}".format(self.convToBytes(self.stopPos)))
        self.ser.write(mess)
        self.couche = 1
        time.sleep(0.5)

    def boucle(self):
        if self.enPause:
            self.enPause = False
            if self.direction == 1:
                mess = [1, 4, 0, 0] + self.convToBytes(self.startPos)
                self.ser.write(mess)
            else:
                mess = [1, 4, 0, 0] + self.convToBytes(self.stopPos)
                self.ser.write(mess)
            time.sleep(0.5)

        time.sleep(0.2)
        mess = [1, 6, 3, 0, 0, 0, 0, 0]
        resp = self.ser.readWrite(mess)
        if resp[0:9] == [0, 2, 1, 100, 6, 0, 0, 0, 0]:
            mess = [1, 6, 1, 0, 0, 0, 0, 0]
            resp = self.ser.readWrite(mess)
            print("resp:", resp)
            if 1 == self.direction:
                self.direction = 2
                mess = [1, 4, 0, 0] + self.convToBytes(self.stopPos)
                self.ser.write(mess)
                self.couche += 1
            else:
                self.direction = 1
                mess = [1, 4, 0, 0] + self.convToBytes(self.startPos)
                self.ser.write(mess)
                self.couche += 1
        time.sleep(0.1)

    def pause(self):
        if not self.enPause:
            msg = [1, 3, 0, 0, 0, 0, 0, 0]
            self.ser.write(msg)
        self.enPause = True
        time.sleep(0.1)

    def postBoucle(self):
        msg = [1, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.ser.write(msg)
        time.sleep(0.1)
        mess = [1, 5, 4, 0] + self.convToBytes(1000)
        self.ser.write(mess)
        self.direction = 0
        self.configurate = False

    def convToBytes(self, integer):
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
