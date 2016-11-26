#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import Queue

class ThreadsConnector:
    """ Contrôle la communication entre thread.
    Classe inspirée de discutions sur le site:
    www.stackoverflow.com
    """
    COMPTEUR = 0
    def __init__(self,name = None):
        """ Initialisation de l'objet """
        self.messages   = Queue.Queue()
        if (name == None):
            self.name = 'ThreadsConnector - {}'.format(ThreadsConnector.COMPTEUR)
        else:
            self.name = name
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Démarrage de {}'.format(self.name))
        ThreadsConnector.COMPTEUR += 1

    def put_message(self, msg):
        """ Just a wrapper to Queue.put_nowait() """
        self.messages.put_nowait(msg)

    def is_empty(self):
        return self.messages.empty()

    def get_wait(self,time):
        try:
            return self.messages.get(True,time)
        except Queue.Empty:
            pass

    def get_message(self):
        """ Just a wrapper to Queue.get_nowait() """
        return self.messages.get_nowait()

    
    def flush(self):
        """Pour vider la queue"""
        while not self.messages.empty():
            try:
                self.messages.get_nowait()
            except Queue.Empty:
                pass
            