#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import Tkinter as tk
import os
import logging
import DEFINE
import iFunctions as iF
try:
    import cPickle as pickle
except:
    import pickle


class wBobine(tk.Toplevel):
    """Défini une nouvelle fenêtre de bobine.
    Est utilisé pour ouvrir ou créer une nouvelle bobine.
    """
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.logger = logging.getLogger(self.__class__.__name__)
        L, H, X, Y = iF.geoliste((self.parent).geometry())
        self.geometry("%dx%d%+d%+d" % (600, 400, X + 50, Y + 100))
        partDATA = tk.LabelFrame(self, text="Projet", padx=10, pady=10,
                                 relief=tk.GROOVE)
        partL = tk.Frame(self)

        self.vecteur09 = range(0, 10)

        self.champ_LabelDATA = []
        self.champ_VarDATA = []
        self.INFO = DEFINE.dBOBINE.copy()
        self.dicoBobine = {}
        for clef, valeur in (DEFINE.dBOBINE).items():
            (self.dicoBobine)[clef] = tk.StringVar()

        for i in DEFINE.BOBINE_order:
            self.champ_LabelDATA.append(tk.Label(partDATA,
                                        text=DEFINE.TRANSLATE_BOBINE[i] + " :")
                                        )
            self.champ_VarDATA.append(tk.Entry(partDATA, width=16,
                                      textvariable=(self.dicoBobine)[i]))

        for i in self.vecteur09:
            (self.champ_LabelDATA)[i].grid(row=i, column=0, sticky="E")

        for i in self.vecteur09:
            (self.champ_VarDATA[i]).grid(row=i, column=1)

        self.IDbobine = tk.StringVar()
        self.IDbobine.set("ID bobine")
        (self.champ_VarDATA[4]).configure(textvariable=self.IDbobine,
                                          state=tk.DISABLED)

        self.boutongenerateID = tk.Button(partDATA, text="Générer ID",
                                          anchor=tk.W, width=16,
                                          command=self.updateID)
        self.boutongenerateID.grid(row=4, column=2)

        self.buttonChgID = tk.Button(partDATA, text="Modifier ID",
                                     anchor=tk.W, width=16,
                                     command=self.modID)
        self.buttonChgID.grid(row=4, column=3)

        partDATA.pack(side=tk.TOP)
        boutonOk = tk.Button(partL, text="Valider", anchor=tk.W,
                             command=self.validate)
        boutonOk.pack()
        partL.pack(expand=1, fill=tk.BOTH, side=tk.BOTTOM)

    def validate(self):
        try:
            f = open('BOBINE/'+str((self.IDbobine).get())+'.bobine', 'w')
        except:
            self.logger.error("Impossible de créer le fichier {}.bobine".
                              format(str((self.IDbobine).get())))
        else:
            for i in self.vecteur09:
                var = DEFINE.BOBINE_order[i]
                self.INFO[var] = (self.champ_VarDATA[i]).get()
                if self.champ_VarDATA[DEFINE.BOBINE_order.index(DEFINE.NINTERRUPT)].get() == "":
                    self.INFO[DEFINE.NINTERRUPT] = -1
            pickle.dump(self.INFO, f)
            self.logger.info("Bobine {} créer".format(str((self.IDbobine).get())))
            f.close()
        (self.parent).loadBobine(str((self.IDbobine).get()))
        self.destroy()

    def updateID(self):
        text = []
        for indice, champ in enumerate(self.champ_VarDATA):
            text.append(champ.get())

        (self.IDbobine).set('{}_{}_{}_{}'.format(text[0][0:2], text[1][0:3],
                                                 text[2], text[3]))

    def modID(self):
        (self.champ_VarDATA[4]).config(state=tk.NORMAL)
        (self.buttonChgID).config(text="Valider ID", command=self.validateID)

    def validateID(self):
        (self.champ_VarDATA[4]).config(state=tk.DISABLED)
        (self.buttonChgID).config(text="Modifier ID", command=self.modID)


class openWBobine(wBobine):
    """Défini une nouvelle fenêtre. Cette fenêtre va permettre d'ouvrir une
    nouvelle bobine"""
    def __init__(self, parent, filename):
        wBobine.__init__(self, parent)
        self.parent = parent
        try:
            f = open(filename, 'r')
        except:
            self.destroy()
            print("Impossible d'ouvrir le fichier")
            self.logger.error("Impossible d'ouvrir le fichier {}.bobine".
                              format(filename))
        else:
            self.logger.info('Bobine "{}" chargée'.format(filename))
            self.focus_set()
            path = filename
            name = os.path.basename(path)
            name = name.replace('.bobine', '')
            self.title("Bobine : " + str(name))
            dicoTmp = pickle.load(f)
            for clef, val in dicoTmp.items():
                self.dicoBobine[clef].set(val)
            self.logger.debug(dicoTmp)
            for clef, val in dicoTmp.items():
                self.dicoBobine[clef].set(val)
            f.close()
            self.updateID()


class newWBobine(wBobine):
    """Défini une nouvelle fenêtre. Cette fenêtre va permettre de créer une
    nouvelle bobine"""
    def __init__(self, parent):
        wBobine.__init__(self, parent)
        self.parent = parent
        self.title("Nouvelle bobine")
