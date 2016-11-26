#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import Moteur
import time
import RPi.GPIO as GPIO


class CompteTour(Moteur.Moteur):
    """Cette classe permet de gérer le compte-tour.
        tour:           enregistre le nombre de tour effectué
        compteurRPM:    enregistre la vitesse (en tour par minutes)
    """
    def __init__(self, ser, memory, runEvent, nouvelleBobineEvent, errorEvent):
        Moteur.Moteur.__init__(self, runEvent, nouvelleBobineEvent, 'Compte-tour')
        self.ser = ser
        self.mem = memory
        self.runEvent = runEvent
        self.nouvelleBobine = nouvelleBobineEvent
        self.errorEvent = errorEvent

        #   nombre de tour déjà effectué
        self.tour = 0
        GPIO.setup(16, GPIO.IN)
        GPIO.setup(20, GPIO.IN)
        GPIO.setup(21, GPIO.IN)

        #   Pour incrémenter artificiellement le compte-tours.
        #   On doit utiliser le compte-tours réel
        self.t0 = 0
        self.t1 = 0
        self.s0 = 0
        self.s1 = 0
        self.rpm = 0
        self.compteurRPM = 0
        self.p0 = 0
        self.p1 = 0

    def position(self):
        """Cette fonction retourne:
            soit l'une des huit positions
            soit zéro si le code de grey"""
        if (GPIO.input(16) == 0 and GPIO.input(20) == 0 and GPIO.input(21) == 0):
            return 8
        elif (GPIO.input(16) == 1 and GPIO.input(20) == 0 and GPIO.input(21) == 0):
            return 7
        elif (GPIO.input(16) == 1 and GPIO.input(20) == 1 and GPIO.input(21) == 0):
            return 6
        elif (GPIO.input(16) == 0 and GPIO.input(20) == 1 and GPIO.input(21) == 0):
            return 5
        elif (GPIO.input(16) == 0 and GPIO.input(20) == 1 and GPIO.input(21) == 1):
            return 4
        elif (GPIO.input(16) == 1 and GPIO.input(20) == 1 and GPIO.input(21) == 1):
            return 3
        elif (GPIO.input(16) == 1 and GPIO.input(20) == 0 and GPIO.input(21) == 1):
            return 2
        elif (GPIO.input(16) == 0 and GPIO.input(20) == 0 and GPIO.input(21) == 1):
            return 1
        else:
            print("[ERROR - code de Gray inconnu]")
            self.l.error("Code de Gray inconnu: {},{},{}".format(GPIO.input(16), GPIO.input(20),GPIO.input(21)))
            return 0

    def configure(self, x):
        self.configurate = x

    def preBoucle(self):
        self.t0 = 0
        self.t1 = 0
        self.s0 = self.position()
        self.s1 = self.position()
        self.tour = 0
        self.compteurRPM = 0
        self.p0 = 0
        self.p1 = 0
        self.tourPrec = 0

    def boucle(self):
        self.s0 = self.position()
        time.sleep(0.05)
        self.s1 = self.position()
        if self.s1 < self.s0:
            self.s1 = self.s1 + 8

        self.tour = self.tour + ((self.s1 - self.s0)*(1/8.0))
        if (self.tour - self.tourPrec) > 0.5:
            self.t1 = time.time()
            dp = self.tour - self.tourPrec
            self.tourPrec = self.tour
            dt = self.t1 - self.t0
            self.t0 = self.t1

            #   On exclu les outsiders
            if (dp/dt)*60 < 135:
                self.rpm = (dp/dt)*60
            else:
                self.rpm = 135

    def pause(self):
        self.boucle()

    def postBoucle(self):
        self.configurate = False
