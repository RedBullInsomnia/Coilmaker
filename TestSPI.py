#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Partie principale du programme. Lance les autres objets"""
import logging
import threading

import RPi.GPIO as GPIO
import spidev

import random
import time

import mem
import iFunctions as F
import myDataRecord
import ThreadsConnector as TC
import mySpi
import Interface as iF
import compteTour
import core
import sondeHall as SH
import mouvement
import DEFINE

GPIO.setmode(GPIO.BCM)
#GPIO.setup(18,GPIO.OUT,initial = GPIO.HIGH) #Commentee car pas de shield a remettre
#   Nécessaire pour activer le levelShifter et permettre la com RPi <-> PIC
#GPIO.setup(27,GPIO.IN)

#spi = mySpi.LockSpi()
spi = spidev.SpiDev()
spi.open(0,0)

print "Mise à zéro machine"
mess = [161,5,203,0,0,0,7,255]
spi.xfer2(mess)
time.sleep(0.1)
mess = [161,5,205,0,0,0,0,7]
spi.xfer2(mess)
time.sleep(0.1)
mess =[161,1,0,0,0,0,7,255]
spi.xfer2(mess)
time.sleep(0.1)
resp = [0,0,0,0,0,0,0,0,0,0]
boucle = True
while boucle:
    mess = [161,6,3,0,0,0,0,0]
    F.addChecksum(mess)
    spi.xfer2(mess)
    time.sleep(0.05)
    print 'Mess' , mess
    """if GPIO.input(27):
        resp = [81,0,0,0,0,0,0,0,0,0]
        resp = spi.xfer2(resp)
        """
    print "RESP = " , resp
    if resp[5:9] == [0,0,0,0]:
        boucle = False
        boucle = True

    time.sleep(0.5)
    print 'ok'

