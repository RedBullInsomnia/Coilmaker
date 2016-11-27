#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from myThreads import Thread
import time


class Moteur(Thread):
    """Classe de base sur laquelle on construit les moteurs (classe fille)"""
    count = 0

    def __init__(self, run_event, newCoil_event, name=None):
        Thread.__init__(self, name)
        if name is None:
            self.name = 'Moteur - {}'.format(Moteur.count)
        else:
            self.name = name

        self.run_event = run_event
        self.newCoil = newCoil_event

        self.configurate = False
        self.l.info('Instanciation de {}'.format(self.name))

    def run(self):
        while not self.stop:  # Stop est dans le "myThreads"
            while ((not self.newCoil.isSet()) and(not self.stop)):
                self.newCoil.wait(1.0)

            self.l.debug(('On attend les configurations'))
            while ((not self.stop) and (not self.configurate)):
                time.sleep(0.1)
                self.configurate = self.config()
            self.preBoucle()
            while ((self.newCoil.isSet()) and(not self.stop)):
                # On tourne dans la boucle
                while ((not self.run_event.isSet()) and (not self.stop)):
                    self.pause()
                self.boucle()
            self.postBoucle()

    def config(self):
        return self.configurate

    def preBoucle(self):
        pass

    def boucle(self):
        pass

    def pause(self):
        time.sleep(0.1)

    def postBoucle(self):
        self.configurate = False
