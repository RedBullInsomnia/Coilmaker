#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Partie principale du programme. Lance les autres objets"""
import logging
import threading

import RPi.GPIO as GPIO

import random
import time

import mem
import iFunctions as F
import myDataRecord
import ThreadsConnector as TC
import Interface as iF
import compteTour
import core
import mySerial
import sondeHall as SH
import mouvement
import DEFINE




if __name__ == '__main__':

########################################
#
#       Phase d'initialisation
#
########################################
    #   On initialise le processus de logging
    
    #   définition d'un loggeur qui enregistre tout dans le fichier
    ROOTLEVEL = logging.DEBUG
    # ROOTLEVEL = logging.INFO
    formatter = logging.Formatter('%(asctime)s [%(levelname)8s] %(name)16s - %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(ROOTLEVEL)
    rootHandler = logging.FileHandler('LOG/log%s.log'%str(int(time.time())))
    rootHandler.setLevel(ROOTLEVEL)
    rootHandler.setFormatter(formatter)
    rootLogger.addHandler(rootHandler)
    logging.addLevelName(15, 'DATA')
    rootLogger.debug('Le processus de log principal a été initialisé')
    rootLogger.info('Phase d\'initialisation')
    #   On crée un loggeur pour les données 
    DATALOGGER = 'datalogger'
    dataLogger = myDataRecord.dataRecord(DATALOGGER)
    rootLogger.debug('Le processus de log secondaire est activé')
    rootLogger.info('Les processus de log sont actif')

    GPIO.setmode(GPIO.BCM)
   
 

    ser = mySerial.LockSerial()

    rootLogger.info('Serial et GPIO actif')
    #   Initialisation des objets
    rootLogger.info('Début de la construction des différents objets')
    

    
    mwOut = TC.ThreadsConnector()
    mwIn = TC.ThreadsConnector()
    
    rootLogger.info('Création des évenements')
    runEvent = threading.Event()
    nouvelleBobineEvent = threading.Event()
    errorEvent = threading.Event()
    rootLogger.info('Création des éléments')
    
    gMem = mem.Mem()
    
    p = mouvement.Position(ser,gMem,runEvent,nouvelleBobineEvent,errorEvent)
    sonde = SH.SondeHall(ser,gMem,runEvent,nouvelleBobineEvent,errorEvent)
    CT = compteTour.CompteTour(ser,gMem,runEvent,nouvelleBobineEvent,errorEvent)
    core = core.Core(ser,gMem,runEvent,nouvelleBobineEvent,errorEvent,mwOut,mwIn,dataLogger)
    gMem.setPos(p)
    gMem.setCore(core)
    gMem.setCT(CT)
    gMem.setSH(sonde)
    mw = iF.MainWindow(mwIn,mwOut,core,dataLogger,runEvent,nouvelleBobineEvent,errorEvent)    
    
########################################
#
#       Programme principal
#
########################################

    
    #  On lance le programme principal
    rootLogger.info('Début du programme principal')
    rootLogger.info('Mise à zéro moteur')
    rootLogger.debug('Stall Detection actif')
    print "Mise à zéro machine"

    mess = [1,28,203,0,0,0,7,255]
    F.addChecksum(mess)
    ser.write(mess)
    time.sleep(0.1)

    boucle = True
    while boucle:
        mess = [1,28,0,0,0,0,0,40]
        F.addChecksum(mess)
        resp = ser.readWrite(mess)
        print "resp = "
        print resp
        if resp[4:8] == [0,0,0,40]:
            boucle = False
        time.sleep(1)

    mess = [1,5,205,0,0,0,0,0]
    F.addChecksum(mess)
    ser.write(mess)
    time.sleep(0.1)
    mess = [1,5,203,0,0,0,0,0]
    F.addChecksum(mess)
    ser.write(mess)
    time.sleep(0.1)
    mess = [1,5,1,0,0,0x7F,0xFF,0xFF]
    F.addChecksum(mess)
    ser.write(mess)
    time.sleep(0.1)
    mess = [1,4,0,0,0,0x7F,0x00,0x00]
    F.addChecksum(mess)
    ser.write(mess)
    rootLogger.debug('Stall Detection actif')
    rootLogger.info('Fin de la mise à zéro moteur')
    
    CT.start()
    core.start()
    sonde.start()
    p.start()
    
    mw.mainloop()
    
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
    
