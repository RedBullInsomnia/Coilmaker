#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import random
import time
import DEFINE
import RPi.GPIO as GPIO
import Moteur
import iFunctions as iF


class Position(Moteur.Moteur):
    def __init__(self,ser,mem,runEvent,nouvelleBobineEvent,errorEvent):
        """Permet le déplacement."""
        Moteur.Moteur.__init__(self,runEvent,nouvelleBobineEvent, name ='Deplacement')
        self.ser = ser
        self.mem = mem
        self.errorEvent = errorEvent
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
        mess = [1,6,1,0,0,0,0,0]
        iF.addChecksum(mess)
        #time.sleep(0.05)
        resp = self.ser.readWrite(mess)
	print("respyyy: ",resp)
        self.startPos = resp[4]*256**3 + resp[5]*256**2 +resp[6]*256 +resp[7]
        self.stopPos = max(0,int(self.startPos - float(str(self.mem.core.dicoBobine[DEFINE.LBOBINE]).replace(',','.'))*1000*63.952))
	print("stopposyyy: ",self.stopPos)
        time.sleep(0.1)
        #   Vitesse avance - par défaut: 1,2 * DFIL
        mess = [1,5,4,0] + iF.convertToOctet(int(0.2*float(str(self.mem.core.dicoBobine[DEFINE.DFIL]).replace(',','.'))*2.047))
        iF.addChecksum(mess)
        self.ser.write(mess)
        time.sleep(0.1)
        self.l.info("Moteur translation configuré")
        self.direction = 2
        self.configurate = True
        
    def preBoucle(self):
        mess = [1,4,0,0] + iF.convertToOctet(self.stopPos)
	print("messy:", mess)
        print "Start pos: {}".format(iF.convertToOctet(self.startPos))
        print "Stop pos: {}".format(iF.convertToOctet(self.stopPos))
        iF.addChecksum(mess)
        self.ser.write(mess)
        self.couche = 1
        time.sleep(0.5)
            
    def boucle(self):
        if self.enPause:
            self.enPause = False
            if self.direction == 1:
                mess = [1,4,0,0]+iF.convertToOctet(self.startPos)
                iF.addChecksum(mess)
                self.ser.write(mess)
            else:
                mess = [1,4,0,0]+iF.convertToOctet(self.stopPos)
                iF.addChecksum(mess)
                self.ser.write(mess)
            time.sleep(0.5)

        time.sleep(0.2)
        mess = [1,6,3,0,0,0,0,0]
        iF.addChecksum(mess)
        resp = self.ser.readWrite(mess)
        if resp[0:9] == [0,2,1,100,6,0,0,0,0]:
            mess = [1,6,1,0,0,0,0,0]
            iF.addChecksum(mess)
            resp = self.ser.readWrite(mess)
            print resp
            if self.direction == 1:
                self.direction = 2
                mess = [1,4,0,0] + iF.convertToOctet(self.stopPos)
                iF.addChecksum(mess)
                self.ser.write(mess)
                self.couche += 1
            else:
                self.direction = 1
                mess = [1,4,0,0] + iF.convertToOctet(self.startPos)
                iF.addChecksum(mess)
                self.ser.write(mess)
                self.couche += 1
        time.sleep(0.1)
 
        
    def pause(self):
        if (self.enPause == False):
            self.ser.write([1,3,0,0,0,0,0,0,4])
        self.enPause = True
        time.sleep(0.1)
 
    def postBoucle(self):
        self.ser.write([1,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x04])
        time.sleep(0.1)
        mess = [1,5,4,0] + iF.convertToOctet(1000)
        iF.addChecksum(mess)
        self.ser.write(mess)
        self.direction = 0
        self.configurate = False
