#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import myThreads
import random
import time


class Moteur(myThreads.Thread):
    """Classe de base sur laquelle on construit les moteurs (classe fille)"""
    COMPTEUR  = 0
    def __init__(self,runEvent,nouvelleBobineEvent, name = None):
        myThreads.Thread.__init__(self,name)
        if (name == None):
            self.name = 'Moteur - {}'.format(Moteur.COMPTEUR)
        else:
            self.name = name
        
        self.runEvent = runEvent
        self.nouvelleBobine = nouvelleBobineEvent

        self.configurate = False
        self.l.info('Instanciation de {}'.format(self.name))

    def run(self):
        while not self.stop :#  Stop est dans le "myThreads"
            while ((not self.nouvelleBobine.isSet()) and(not self.stop)):
                self.nouvelleBobine.wait(1.0)#  On attend pour démarrer une bobine
            
            self.l.debug(('On attend les configurations'))            
            while ((not self.stop) and (not self.configurate)) :
                time.sleep(0.1)
                self.configurate = self.config()
            self.preBoucle()    
            while ((self.nouvelleBobine.isSet()) and(not self.stop)):
            #   On tourne dans la boucle
                while ((not self.runEvent.isSet()) and (not self.stop)):#On est dans une pause
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

