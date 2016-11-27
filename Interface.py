#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import Bobine as iB
import Tkinter as tk
try:
    import cPickle as pickle
except:
    import pickle
import threading
import logging
import tkFileDialog
import tkMessageBox
import Queue
import DEFINE
import time
import RPi.GPIO as GPIO


class MainWindow(tk.Tk):
    """Classe qui va gérer la fenêtre principale.
    """
    def __init__(self, connDown, connUp, core, dataLogger, run_event,
                 newCoil_event, error_event, parent=None):
        """Constructeur de la fenêtre principale"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initialisation de l'interface")
        self.connUp = connUp
        self.connDown = connDown
        self.runE = run_event
        self.nouvelleBobine = newCoil_event
        self.error_event = error_event
        self.core = core
        self.bobineEnCours = False
        self.dataLogger = dataLogger
        self.stateLed = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)
        self.initInterface(parent)
        self.periodiccall()

    def initInterface(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("Embobineuse")
        self.geometry("900x600+42+42")

        self.dicoBobine = {}
        self.dicoVariables = {}

        for clef, valeur in (DEFINE.dBOBINE).items():
            (self.dicoBobine)[clef] = tk.StringVar()
        for clef, valeur in (DEFINE.VARIABLES).items():
            (self.dicoVariables)[clef] = tk.StringVar()

        self.sGAP = tk.StringVar()
        self.sRPM = tk.StringVar()

        partH = tk.Frame(self)
        partL = tk.Frame(self)
        partDATA = tk.LabelFrame(partH, text="Projet", padx=10, pady=10,
                                 relief=tk.GROOVE)
        partOUTPUT = tk.LabelFrame(partH, text="OUTPUTS", padx=10, pady=10,
                                   relief=tk.GROOVE)
        partORDER = tk.LabelFrame(partL, text="Commandes", padx=10, pady=10,
                                  relief=tk.GROOVE)

        for clef, valeur in (self.dicoVariables).items():
            valeur.set("")

        self.champ_LabelDATA = []
        self.champ_VarDATA = []

        for i in DEFINE.BOBINE_order:
            self.champ_LabelDATA.append(tk.Label(partDATA, state=tk.DISABLED,
                                        text=DEFINE.TRANSLATE_BOBINE[i] + " :"))
            self.champ_VarDATA.append(tk.Label(partDATA, state=tk.DISABLED,
                                               textvariable=(self.dicoBobine)[i]))

        for i, champ in enumerate(self.champ_LabelDATA):
            champ.grid(row=i, column=0, sticky="W")

        for i, champ in enumerate(self.champ_VarDATA):
            champ.grid(row=i, column=1, sticky="W")

        self.champ_LabelOUTPUT = []
        self.champ_VarOUTPUT = []
        for i in xrange(6):
            self.champ_LabelOUTPUT.append(tk.Label(partOUTPUT, state=tk.DISABLED, text=DEFINE.TRANSLATE_VARIABLES[DEFINE.VARIABLES_order[i]] + " :"))
            self.champ_VarOUTPUT.append(tk.Label(partOUTPUT, state=tk.DISABLED, textvariable=(self.dicoVariables)[DEFINE.VARIABLES_order[i]]))

        for i, champ in enumerate(self.champ_LabelOUTPUT):
            champ.grid(row=i, column=0, sticky="W")

        for i, champ in enumerate(self.champ_VarOUTPUT):
            champ.grid(row=i, column=1, sticky="W")

        self.boutonSTART = tk.Button(partORDER, text="START", anchor=tk.W,
                                     width=16, state=tk.DISABLED,
                                     command=self.go)
        self.boutonSTOP = tk.Button(partORDER, text="PAUSE", anchor=tk.W,
                                    width=16, state=tk.DISABLED,
                                    command=self.pause)
        self.boutonLED = tk.Button(partORDER, text="LED", anchor=tk.W,
                                   width=16, command=self.led)
        self.boutonHALT = tk.Button(partORDER, text="STOP + Rapport",
                                    anchor=tk.W, width=16, state=tk.DISABLED,
                                    command=self.stopBob)
        self.sliderGAPlabel = tk.Label(partORDER, text="Avance (um/tour): ",
                                       state=tk.DISABLED)
        self.sliderRPMlabel = tk.Label(partORDER,
                                       text="Vitesse de rotation (rpm): ",
                                       state=tk.DISABLED)

        self.GAP = tk.Entry(partORDER, width=8, textvariable=self.sGAP,
                            state=tk.DISABLED)
        self.RPM = tk.Entry(partORDER, width=8, textvariable=self.sRPM,
                            state=tk.DISABLED)
        self.GAPbutton = tk.Button(partORDER, text="valider", anchor=tk.W, width=8, state = tk.DISABLED, command = self.updateGAP)
        self.RPMbutton = tk.Button(partORDER, text="valider", anchor=tk.W, width=8, state = tk.DISABLED, command = self.updateRPM)
        self.sliderGAP = tk.Scale(partORDER, from_=0, to=200, length= 500, tickinterval = 50,orient=tk.HORIZONTAL,state= tk.DISABLED, command = self.getGAP)
        self.sliderRPM = tk.Scale(partORDER, from_=0, to=120, length= 500, tickinterval = 15,bigincrement= 15, orient=tk.HORIZONTAL,state= tk.DISABLED, command = self.getRPM)

        self.boutonSTOP.grid(row=0, column=0)
        self.boutonSTART.grid(row=0, column = 1)
        self.boutonLED.grid(row=3, column = 0)
        self.boutonHALT.grid(row=3, column = 1)
        self.sliderGAPlabel.grid(row=1, column = 0)
        self.sliderRPMlabel.grid(row=2, column = 0)
        self.sliderGAP.grid(row=1, column = 1)
        self.sliderRPM.grid(row = 2, column = 1)
        self.GAP.grid(row = 1, column = 3)
        self.RPM.grid(row = 2, column = 3)
        self.GAPbutton.grid(row=1, column=4)
        self.RPMbutton.grid(row=2, column=4)

        partH.pack(expand=1, fill=tk.BOTH, side=tk.TOP)
        partL.pack(expand=1, fill =tk.BOTH, side =tk.BOTTOM)

        partDATA.pack(expand=1, fill=tk.BOTH, side=tk.LEFT)
        partOUTPUT.pack(expand = 1, fill = tk.BOTH,side = tk.RIGHT)
        partORDER.pack(expand = 1, fill = tk.BOTH,side = tk.BOTTOM)

        #   Les menus
        menubar = tk.Menu(self)
        coilmenu = tk.Menu(menubar, tearoff=0)
        coilmenu.add_command(label="Nouveau", command=self.newBobine)
        coilmenu.add_command(label="Ouvrir", command=self.openBobine)
        coilmenu.add_separator()
        coilmenu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Bobine", menu=coilmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="A propos de...", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
        self.logger.info("Interface chargée")

    def about(self):
        message = """Ce programme a été écrit par Nathan Maquet
        Ce programme fait partie du TFE:
        "Conception et réalisation d'une bobineuse automatique de précision"
        """
        tkMessageBox.showinfo("A propos de ...", message)

    def newBobine(self):
        return iB.newWBobine(self)

    def openBobine(self):
        filename = tkFileDialog.askopenfilename(initialdir='BOBINE')
        if (filename):
            return iB.openWBobine(self, filename)

    def loadBobine(self, filename):
        self.core.loadBobine(filename)
        try:
            f = open('BOBINE/'+filename+'.bobine', 'r')
        except:
            print "impossible d'ouvrir le fichier"
            self.logger.error("Impossible d'ouvrir le fichier")
        else:
            self.logger.info('Bobine "{}" chargée'.format(filename))
            dicoTmp = pickle.load(f)
            for clef, val in dicoTmp.items():
                self.dicoBobine[clef].set(val)
            self.logger.debug(dicoTmp)
            f.close()
            self.changeState()
            self.sliderGAP.config(from_=0.90* int(self.dicoBobine[DEFINE.DFIL].get()), to=1.40* int(self.dicoBobine[DEFINE.DFIL].get()),tickinterval = int(self.dicoBobine[DEFINE.DFIL].get())/20)
            self.sliderGAP.set(int(self.dicoBobine[DEFINE.DFIL].get()) + int(int(self.dicoBobine[DEFINE.DFIL].get())/5.0))
            self.sliderRPM.set(10)
            self.bobineEnCours = False
            for clef, valeur in (self.dicoVariables).items():
                valeur.set("")
            # tkMessageBox.showinfo(
                # message= 'Placer la poutre en position {}'.format(1 if (int(self.dicoBobine[DEFINE.DFIL].get()) < 100) else 2),
                # icon= 'warning',
                # title= 'Réglage poutre flexion')

    def updateGAP(self):
        x = self.GAP.get()
        tmpValue = float(x)
        self.sliderGAP.set(x)
        self.connUp.put_message((DEFINE.AVANCE, str(tmpValue)),)

    def getGAP(self, x):
        self.sGAP.set(x)
        self.connUp.put_message((DEFINE.AVANCE, str(x)),)

    def getRPM(self, x):
        self.sRPM.set(x)
        self.connUp.put_message((DEFINE.RPM, str(x)),)

    def updateRPM(self):
        x = self.RPM.get()
        tmpValue = float(x)
        self.sliderRPM.set(x)
        self.connUp.put_message((DEFINE.RPM, str(tmpValue)),)

    def led(self):
        if self.stateLed:
            self.stateLed = False
            GPIO.output(24, GPIO.LOW)
        else:
            self.stateLed = True
            GPIO.output(24, GPIO.HIGH)

    def changeState(self):
        for indice, champ in enumerate(self.champ_LabelDATA):
            champ.config(state=tk.NORMAL)
        for indice, champ in enumerate(self.champ_VarDATA):
            champ.config(state=tk.NORMAL)
        for indice, champ in enumerate(self.champ_LabelOUTPUT):
            champ.config(state=tk.NORMAL)
        for indice, champ in enumerate(self.champ_VarOUTPUT):
            champ.config(state=tk.NORMAL)
        self.boutonSTART.config(state=tk.NORMAL, text="Démarrer bobine")
        self.boutonLED.config(state=tk.NORMAL)
        self.boutonHALT.config(state=tk.NORMAL)
        self.sliderGAP.config(state=tk.NORMAL)
        self.sliderRPM.config(state=tk.NORMAL)
        self.sliderGAPlabel.config(state=tk.NORMAL)
        self.sliderRPMlabel.config(state=tk.NORMAL)
        self.GAP.config(state=tk.NORMAL)
        self.RPM.config(state=tk.NORMAL)
        self.GAPbutton.config(state=tk.NORMAL)
        self.RPMbutton.config(state=tk.NORMAL)

    def go(self):
        self.logger.info('Pression sur le bouton "START"')
        self.dataLogger.event('Pression sur le bouton "START"')
        self.boutonSTART.config(state=tk.DISABLED)
        self.boutonSTOP.config(state=tk.NORMAL)
        if self.bobineEnCours:
            self.core.resumeBobine()
        else:
            self.core.startBobine()
            self.updateGAP()
            self.updateRPM()
            self.bobineEnCours = True
            self.boutonSTART.config(text="Continuer")

    def pause(self):
        self.logger.info('Pression sur le bouton "PAUSE"')
        self.dataLogger.event('Pression sur le bouton "PAUSE"')
        self.boutonSTOP.config(state=tk.DISABLED)
        self.boutonSTART.config(state=tk.NORMAL)
        self.core.pauseBobine()

    def periodiccall(self):  # On vérifie 25 fois par seconde
        self.checkupdate()
        if ((not self.nouvelleBobine.isSet()) and (self.bobineEnCours) and not self.error_event.isSet()):
            self.bobineEnCours = False
            tkMessageBox.showinfo(
                message='La bobine est terminée !',
                icon='info',
                title='Bobinage de la bobine : Succès')
        if (self.error_event.isSet()):
            tkMessageBox.showerror('ERREUR !', 'Une erreur est survenue !')
            self.dataLogger.event('Une erreur est survenue !')
            self.bobineEnCours = False
            self.error_event.clear()

        self.after(40, self.periodiccall)

    def checkupdate(self):
        while not self.connDown.is_empty():
            try:
                msg = self.connDown.get_message()
                if type(msg) == type((0,0)):
                    self.logger.info('Mise en pause automatique')
                    self.dataLogger.event("Pause programmée de la bobine")
                    self.boutonSTOP.config(state=tk.DISABLED)
                    self.boutonSTART.config(state=tk.NORMAL)
                    self.core.pauseBobine()
                    tkMessageBox.showinfo(message='La bobine est en pause!',
                                          icon='info',
                                          title='Attente de l\'opérateur')
                if type(msg) == type({0:0}):
                    for clef, valeur in msg.items():
                        if clef == DEFINE.TLEFT:
                            (self.dicoVariables[clef]).set(valeur)
                        else:
                            (self.dicoVariables[clef]).set(round(float(valeur),2))
            except Queue.Empty:
                pass

    def stopBob(self):
        self.core.haltBobine()
