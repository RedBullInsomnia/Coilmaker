#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Partie principale du programme. Lance les autres objets"""
import logging
import threading

import RPi.GPIO as GPIO

import time
import mem
from myDataRecord import dataRecord
from compteTour import CompteTour
from sondeHall import SondeHall
import ThreadsConnector as TC
import Interface as intfc
import core
import mySerial
import mouvement
import DEFINE as df


if __name__ == '__main__':
    """ initialisation """
    #  Log everything to a file
    ROOTLEVEL = logging.DEBUG
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)8s] %(name)16s - %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(ROOTLEVEL)
    rootHandler = logging.FileHandler('LOG/log%s.log' % str(int(time.time())))
    rootHandler.setLevel(ROOTLEVEL)
    rootHandler.setFormatter(formatter)
    rootLogger.addHandler(rootHandler)
    logging.addLevelName(15, 'DATA')
    rootLogger.debug('Le processus de log principal a été initialisé')
    rootLogger.info('Phase d\'initialisation')

    # Datalogger
    DATALOGGER = 'datalogger'
    dataLogger = dataRecord(DATALOGGER)
    rootLogger.debug('Le processus de log secondaire est activé')
    rootLogger.info('Les processus de log sont actifs')

    # Initialisation of GPIO and serial communication
    GPIO.setmode(GPIO.BCM)
    ser = mySerial.LockSerial()
    rootLogger.info('Serial et GPIO actifs')

    # Objects initialisation
    rootLogger.info('Début de la construction des différents objets')

    mwOut = TC.ThreadsConnector()
    mwIn = TC.ThreadsConnector()

    rootLogger.info('Création des événements')
    run_event = threading.Event()
    newCoil_event = threading.Event()
    error_event = threading.Event()
    rootLogger.info('Création des éléments')

    gMem = mem.Mem()

    p = mouvement.Position(ser, gMem, run_event, newCoil_event)
    sonde = SondeHall(ser, gMem, run_event)
    CT = CompteTour(ser, gMem, run_event, newCoil_event)
    core = core.Core(ser, gMem, run_event, newCoil_event, error_event, mwOut,
                     mwIn, dataLogger)
    gMem.setPos(p)
    gMem.setCore(core)
    gMem.setCT(CT)
    gMem.setSH(sonde)
    mw = intfc.MainWindow(mwIn, mwOut, core, dataLogger, run_event,
                          newCoil_event, error_event)

    """ Launching the program """
    rootLogger.info('Début du programme principal')
    rootLogger.info('Mise à zéro moteur')
    rootLogger.debug('Stall Detection actif')
    print("Mise à zéro machine")

    msg = [df.mot_1, df.STOP, 203, 0, 0, 0, 7, 255]
    ser.write(msg)
    time.sleep(0.1)

    loop = True
    while loop:
        msg = [df.mot_1, df.STOP, 0, 0, 0, 0, 0, 40]
        resp = ser.readWrite(msg)
        print("resp : ", resp)
        if resp[4:8] == [0, 0, 0, 40]:
            loop = False
        time.sleep(1)

    msg = [df.mot_1, df.SAP, df.AP_stall, 0, 0, 0, 0, 0]
    ser.write(msg)
    time.sleep(0.1)
    msg = [df.mot_1, df.SAP, df.AP_decay, 0, 0, 0, 0, 0]
    ser.write(msg)
    time.sleep(0.1)
    msg = [df.mot_1, df.SAP, df.AP_currentPos, 0, 0, 0x7F, 0xFF, 0xFF]
    ser.write(msg)
    time.sleep(0.1)
    msg = [df.mot_1, df.MVP, 0, 0, 0, 0x7F, 0x00, 0x00]
    ser.write(msg)
    rootLogger.debug('Stall Detection actif')
    rootLogger.info('Fin de la mise à zéro moteur')

    CT.start()
    core.start()
    sonde.start()
    p.start()

    """ Main loop """
    mw.mainloop()

    """ End of program """
    p._stop()
    core._stop()
    CT._stop()
    sonde._stop()

    time.sleep(1)
    CT.join()
    core.join()
    sonde.join()
    p.join()

    ser.close()
    GPIO.cleanup()

    rootLogger.warning('Fin de l\'application')
    logging.shutdown()
