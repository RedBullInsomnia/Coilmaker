#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging

class dataRecord():
    """Cet objet stock et gère l'enregistrement des données, pour générer des fichiers CSV.
    On surcharge la classe logging. En effet, c'est un loggeur, mais qui continent d'autres choses avec"""
    def __init__(self,name):
        """On crée le loggeur pour récolter les données"""
        #Pour le fichier de données
        self.handlerData = logging.FileHandler('LOG/dataLogger.tmp')
        self.handlerData.setLevel(15)
        self.loggerData = logging.getLogger('d_'+name)
        self.loggerData.setLevel(15)
        self.loggerData.addHandler(self.handlerData)
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.debug('Création du fichier dataHandler.tmp')
        self.dataformatter = logging.Formatter('%(asctime)s;%(message)s')
        #Pour le fichier d'événements
        self.handlerEvent = logging.FileHandler('LOG/dataEvent.tmp')
        self.handlerEvent.setLevel(17)
        self.loggerEvent = logging.getLogger('e_'+name)
        self.loggerEvent.setLevel(17)
        self.loggerEvent.addHandler(self.handlerEvent)
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.debug('Création du fichier dataHandler.tmp')
        self.eventformatter = logging.Formatter('%(asctime)s;%(message)s')
        
    def changeName(self,newName):
        #Pour le fichier de données
        self.loggerData.removeHandler(self.handlerData)
        name = 'RESULTAT/{}-log-d.csv'.format(newName)
        self.handlerData = logging.FileHandler(name)
        self.l.info('Création du fichier {}-log-d.csv'.format(newName))
        self.handlerData.setFormatter(self.dataformatter)
        self.loggerData.addHandler(self.handlerData)
        #Pour le fichier d'événements
        self.loggerEvent.removeHandler(self.handlerEvent)
        self.handlerEvent = logging.FileHandler('RESULTAT/{}-log-e.csv'.format(newName))
        self.l.info('Création du fichier {}-log-e.csv'.format(newName))
        self.handlerEvent.setFormatter(self.eventformatter)
        self.loggerEvent.addHandler(self.handlerEvent)
        
    def log(self, s, lvl = 15):
        self.loggerData.log(lvl, s)
    
    def event(self,s):
        self.loggerEvent.log(17,s)