#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import myThreads
import smbus
import time
import iFunctions as iF


class SondeHall(myThreads.Thread):
    """Permet de lire la tension de la sonde de Hall, et de contrôler le moteur
    La régulation de la tension mécanique dans le fil est également géré par cet objet"""
    def __init__(self, ser, mem, runEvent, nouvelleBobineEvent, errorEvent):
        myThreads.Thread.__init__(self, 'Sonde Hall')
        self.runEvent = runEvent
        self.nouvelleBobine = nouvelleBobineEvent
        self.errorEvent = errorEvent
        self.l.info('Initialisation du Thread - Sonde Hall')
        self.maxRange = 1023.0
        self.mem = mem
        self.ser = ser
        self.consigne = 0
        self.errorRise = False
        self.erreurSonde = 0
        self.sonde = 0
        self.enable = True

    def run(self):
        self.l.info('Démarrage du Thread - Sonde Hall')
        # I2C initialization
        bus = smbus.SMBus(1)
        DEVICE_ADDRESS = 0x4D

        tmp = [0x00, 0x00, 0x00, 0x00]
        tmp = bus.read_word_data(DEVICE_ADDRESS, 0)
        x1 = tmp >> 8
        x2 = (tmp % 256) << 8
        init = x2 + x1

        self.sonde = init
        while not self.stop:
            tmp = bus.read_word_data(DEVICE_ADDRESS, 0)
            x1 = tmp >> 8
            x2 = (tmp % 256) << 8
            tmpSonde = x2 + x1
            self.sonde = tmpSonde
            self.consigne = (self.sonde - init) * 8

            if self.consigne > - 750:
                if (self.consigne > 16):
                    array = [3, 0x01, 0x00, 0x00, 0x00, 0x00,
                             int(int(self.consigne) / 256),
                             int(int(self.consigne) % 256)]
                    self.ser.write(array)
                else:
                    array = [3, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                    self.ser.write(array)
                self.erreurSonde = 0
            else:
                self.erreurSonde += 1

            if (self.erreurSonde > 5) and (not self.errorRise) and self.runEvent and self.enable:
                self.mem.core.EventError("Casse du fil !")
                self.errorRise = True
                msg = [3, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                iF.addChecksum(msg)
                self.ser.write(msg)

            time.sleep(0.1)
            self.l.debug('SondeHall: {}'.format(self.sonde))

    def reset(self):
        self.errorRise = False
        self.erreurSonde = 0
        self.sonde = 0
        self.enable = True

    def _stop(self):
        self.stop = True

    def setEnable(self, e):
        self.enable = e
