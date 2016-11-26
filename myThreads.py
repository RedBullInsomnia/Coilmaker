#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import threading
import logging
import sys
import traceback

class InterruptThread(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class Thread(threading.Thread):
    """Défini une classe d'objet myThread
    
    Attention! Il faut avoir initialisé un fichier LOG avant !!"""
    def __init__(self,name = None):
        threading.Thread.__init__(self)
        if (name != None):
            self.name = name
        self.kill = False
        self.stop = False
        self.l = logging.getLogger(self.__class__.__name__)
        
    def start(self):
        self.run_sav = self.run
        self.run = self.myRun
        threading.Thread.start(self)
        
    def _stop(self):
        self.stop = True

    def myRun(self):
        try:
            self.l.info('Démarrage du myThread - {}'.format(self.getName()))
            self.run_sav()
            self.run = self.run_sav
            if self.kill == True:
                raise InterruptThread('Interruption du myThread - {}'.format(self.getName())) 
        except InterruptThread:
            self.l.exception(('Le myThread - {} a été brutalement arrêté'.format(self.getName())))
        else:
            self.l.info(('Le myThread - {} s\'est correctement terminé'.format(self.getName())))
            
    def kill(self):
        self.kill = True