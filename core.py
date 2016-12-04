#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Fichier 'core'. Contient le coeur du projet"""
import Queue
import os
from myThreads import Thread
import time
import iFunctions as iF
from report import PdfLatex
try:
    import cPickle as pickle
except:
    import pickle
import DEFINE as df
import RPi.GPIO as GPIO


class KeyERROR(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class EventError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Core(Thread):
    def __init__(self, ser, memory, event, newCoil_event, error_event,
                 entrees, sorties, dataLogger):
        Thread.__init__(self)
        self.mem = memory
        self.ser = ser
        self.event = event
        self.newCoil = newCoil_event
        self.error_event = error_event

        self.In = entrees
        self.Out = sorties
        self.dataLogger = dataLogger

        self.error = False

        '''Tant qu'on n'a pas chargé une bobine dans le système, file est vide.
        Les variables sont à zéro et les données bobines vides'''
        self.file = ''
        self.variables = df.VARIABLES.copy()
        self.bobineDemarree = False
        self.enPause = False
        self.dicoBobine = {}
        self.l.debug('Noyau chargé')

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN)

    def run(self):
        self.l.debug('Noyau démarré')
        while (not self.stop):
            # On attend d'avoir chargé une bobine
            if self.file == '':
                time.sleep(1.0)
            else:
                # Une bobine a été chargée
                # Il faut attendre qu'on l'ait démarrée
                self.variables = df.VARIABLES.copy()  # reset variables

                # On fabrique la bobine
                self.makeCoil()
                self.newCoil.clear()
                self.event.clear()

                # A ce stade, on a fini la bobine
                self.bobineDemarree = False
                self.makeReport()
                self.In.flush()
                self.Out.flush()

                # On se remet dans l'état "non chargé"
                self.file = ''
                self.error = False

    def makeReport(self):
        comp = PdfLatex(self.file, self.error, self.variables,
                        self.mem.pos.couche)
        comp.start()

    def makeCoil(self):
        try:
            #   Début de la phase d'initialisation de la procédure
            f = open('RAPPORT/{}.csv'.format(self.file), 'w')
            f.write("time; speed; speedC; tour; avance; sondeHall \n")

            tStart = 0
            tcumul = 0  # total time
            tStop = 0  # time spent paused
            chronoTempsPause = 0

            moyenneCourte = 0
            moyenneLongue = 0
            sizeMCourte = 25  # Taille des tableaux pour les moyennes
            sizeMLongue = 4
            vMoyenneTab = range(0, sizeMCourte)
            vMoyenneTime = range(0, sizeMCourte)
            vMoyenneSpeed = range(0, sizeMCourte)
            vMtab = range(0, sizeMLongue)
            tMtab = range(0, sizeMLongue)
            sHall = range(0, sizeMCourte)

            pauseAlreadyHappen = False
            NTOURS = self.dicoBobine[df.NTOURS]
            NINTER = self.dicoBobine[df.NINTERRUPT]

            self.mem.SH.reset()

            #   Fin de la phase d'initialisation de la procédure
            self.read()  # On consulte les données envoyées par l'interface
            AVANCEprec = float(self.variables[df.AVANCE])
            RPMprec = float(self.variables[df.RPM])
            #   On va attendre d'avoir le start
            while not self.bobineDemarree and not self.stop:
                self.newCoil.wait(1)
                if self.newCoil.isSet() and self.event.isSet():
                    self.bobineDemarree = True

            #   On a le start. On enregistre le début de la bobine dans tStart
            tStart = time.time()
            self.mem.CT.configure(True)
            self.mem.pos.configure()
            tab = [df.mot_2, df.ROR, 0x00, 0x00, 0x00, 0x00,
                   int(int(RPMprec * (2047 / 120.0)) / 256),
                   int(int(RPMprec * (2047 / 120.0)) % 256)]
            self.ser.write(tab)
            sondeHallPrec = self.mem.SH.sonde
            sondeHall = self.mem.SH.sonde
            variableSortie = 0
            increment = 0

            # Main loop #
            while (not self.stop and self.bobineDemarree):
                self.read()  # On lis les données envoyées par l'interface
                if ((int(self.mem.CT.tour) >= int(NTOURS)) and 0 == increment):
                    # Condition d'arrêt
                    self.l.debug('On a fini la bobine')
                    self.stopMotors()
                    self.dataLogger.event("Le programme s'est terminé avec"
                                          "succès")
                    self.mem.SH.setEnable(False)
                    increment = 1

                variableSortie += increment

                '''VariableSortie permets d'attendre que tout s'arrête
                correctement'''
                if variableSortie >= 50:
                    self.bobineDemarree = False
                    self.newCoil.clear()

                # Ici, on entre dans la pause programmée
                if ((int(self.mem.CT.tour) == int(NINTER)) and not pauseAlreadyHappen):
                    self.l.debug('On doit mettre la bobine en pause')
                    self.stopMotors()
                    self.dataLogger.event("Mise en pause automatique de la"
                                          "bobine")
                    self.write(df.MW, (df.CORE, "PAUSE"))
                    pauseAlreadyHappen = True
                    time.sleep(1.0)

                if (not self.event.isSet() and not self.enPause):
                    # On se met en pause
                    self.enPause = True
                    self.stopMotors()
                    chronoTempsPause = time.time()
                    saveRPM = float(self.variables[df.RPM])

                if self.enPause:
                    self.variables[df.RPM] = 0
                    moyenneLongue = 0

                if not self.enPause:
                    tcumul = (time.time() - tStart) - tStop

                if ((self.event.isSet()) and (self.enPause)):
                    # On sort de pause
                    self.enPause = False
                    self.variables[df.RPM] = float(saveRPM)
                    tab = [df.mot_2, df.ROR, 0x00, 0x00, 0x00, 0x00,
                           int(float(saveRPM) * (2047 / 120.0) / 256.0),
                           int(float(saveRPM) * (2047 / 120.0) % 256)]
                    self.ser.write(tab)
                    tStop = tStop + (time.time() - chronoTempsPause)

                if GPIO.input(12) == 1:
                    print "ARRET URGENT"

                self.variables[df.TOUR] = self.mem.CT.tour
                self.variables[df.TTOTAL] = time.time() - tStart
                self.variables[df.TCUMUL] = tcumul
                progress = self.mem.CT.tour * 100 / float(NTOURS)
                self.variables[df.AVANCEMENT] = round(progress, 2)
                self.variables[df.VROT] = self.mem.CT.rpm

                if (moyenneCourte == sizeMCourte):
                    if float(self.variables[df.RPM]) != float(RPMprec):
                        RPMprec = float(self.variables[df.RPM])
                        self.dataLogger.event("Vitesse de rotation: {}".format(RPMprec))
                        tab = [df.mot_2, 1, 0, 0, 0, 0,
                               int(RPMprec * (2047 / 120.0) / 256),
                               int(RPMprec * (2047 / 120.0) % 256)]
                        self.ser.write(tab)
                        tab = [df.mot_1, 5, 4, 0] + iF.convToBytes(int(AVANCEprec * RPMprec * (2047/60000.0)))
                        self.ser.write(tab)

                    if float(self.variables[df.AVANCE]) != float(AVANCEprec):
                        AVANCEprec = float(self.variables[df.AVANCE])
                        self.dataLogger.event("Vitesse d'avance d\'avance: {}".format(AVANCEprec))

                        tab = [df.mot_1, 0x05, 0x04, 0x00] + iF.convToBytes(int(AVANCEprec * RPMprec * (2047/60000.0)))
                        self.ser.write(tab)

                    moyenneCourte = 0
                    if (moyenneLongue == sizeMLongue):
                        vM = ((vMtab[sizeMLongue - 1] - vMtab[0]) /
                              (tMtab[sizeMLongue - 1] - tMtab[0]))
                        if vM == 0.0:
                            self.variables[df.TLEFT] = "Infini"
                        else:
                            self.variables[df.TLEFT] = "{} min {} sec".format((int((float(NTOURS) - self.mem.CT.tour)/vM)/60),(int((float(NTOURS) - self.mem.CT.tour)/vM)%60))
                        moyenneLongue = 0

                    vMoyenne = sum(vMoyenneTab) / sizeMCourte
                    tMoyenne = sum(vMoyenneTime) / sizeMCourte
                    tourMoyen = sum(vMoyenneSpeed) / sizeMCourte
                    hallMoyen = sum(sHall) / sizeMCourte
                    tMtab[moyenneLongue] = tMoyenne
                    vMtab[moyenneLongue] = tourMoyen
                    f.write("{};{};{};{};{};{}\n".format(tMoyenne - tStart,
                                                         vMoyenne,
                                                         RPMprec,
                                                         tourMoyen,
                                                         AVANCEprec,
                                                         hallMoyen*(5/1024.0)))
                    moyenneLongue += 1
                self.write(df.MW, self.variables)

                vMoyenneTab[moyenneCourte] = self.variables[df.VROT]
                vMoyenneTime[moyenneCourte] = time.time()
                vMoyenneSpeed[moyenneCourte] = self.variables[df.TOUR]
                sondeHall = self.mem.SH.sonde
                if (abs(sondeHall - sondeHallPrec) < 128):
                    sHall[moyenneCourte] = sondeHall
                    sondeHallPrec = sondeHall
                else:
                    sHall[moyenneCourte] = sondeHallPrec

                moyenneCourte += 1

                # Le datalogger doit être retravaillé, pour inclure toutes les
                # mesures
                self.dataLogger.log('{};{};{}'.format(self.mem.CT.tour,
                                                      self.variables[df.VROT],
                                                      self.mem.SH.sonde).replace('.', ','))

                time.sleep(0.025)

            #   On a fini la procédure de bobinage
            f.close()
        except:
            self.l.exception("Impossible d'écrire le fichier de data")
            self.dataLogger.event("[ERROR] - (boucle principale)")
            self.error_event.set()
            self.error = True
            self.newCoil.clear()
            self.bobineDemarree = False
        else:
            # Stop the motors !
            self.stopMotors()

    def startBobine(self):
        self.newCoil.set()
        self.event.set()

    def EventError(self, message):
        self.error = True
        self.newCoil.clear()
        self.bobineDemarree = False
        self.error_event.set()
        self.dataLogger.event(message)

    def haltBobine(self):
        self.mem.SH.setEnable(False)
        self.bobineDemarree = False
        self.newCoil.clear()
        self.event.clear()

    def resumeBobine(self):
        self.event.set()

    def pauseBobine(self):
        self.event.clear()

    def loadBobine(self, filename):
        try:
            f = open('BOBINE/'+filename+'.bobine', 'r')
        except:
            print("Impossible d'ouvrir le fichier {}".format(filename+'.bobine'))
            self.l.error("Impossible d'ouvrir le fichier {}".format(filename+'.bobine'))
            self.error_event.set()
        else:
            self.dicoBobine = pickle.load(f)
            self.l.info('Bobine "{}" chargée'.format(filename))
            f.close()
            self.dataLogger.changeName(self.dicoBobine[df.BOBID])
            self.variables[df.AVANCE] = int(self.dicoBobine[df.DFIL] +
                                            (self.dicoBobine[df.DFIL] /
                                            5.0))
            self.file = filename

    def read(self):
        while not self.In.is_empty():
            try:
                msg = self.In.get_message()
                self.variables[msg[0]] = msg[1]
            except Queue.Empty:
                pass

    def write(self, clef, data):
        self.Out.put_message(data)

    def stopMotors(self):
        self.ser.write([df.mot_3, df.MST, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        time.sleep(0.1)
        self.ser.write([df.mot_2, df.MST, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        time.sleep(0.1)
        self.ser.write([df.mot_1, df.MST, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
