#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#   Contient tous les noms de variables

#   Méta-données pour les différents modules
MOTEUR1 = 'moteur1'
HALL = 'sondeHall'
MOTEUR2 = 'moteur2'
POSITION = 'PositionSensor'
MOTEUR3 = 'moteur3'
CT = 'compteTour'
MW = 'mw'

CORE = 'noyau'

#   Noms de paramètres
DFIL = 'diamFil'
LBOBINE = 'longBobine'
NTOURS = 'Ntours'
NINTERRUPT = 'NInterrupt'
FSECU = 'fSecu'
OPID = 'OperateurID'
NPROJET = 'nomProjet'
NOMBOB = 'nomBobine'
NUMBOB = 'numBobine'
BOBID = 'IDbobine'
DNOYAU = 'DNoyau'
#   Noms de variables
VROT = 'vitesseRotation'
TOUR = 'currentTour'
AVANCEMENT = 'avancement'
TLEFT = 'tempsRestant'
TTOTAL = 'tempsTotal'
TCUMUL = 'tempsCumule'


#   Noms de consignes
RPM = 'rpm'
AVANCE = 'distanceEntreSpires'


#   Noms de dico et autres
dBOBINE = {DFIL : "",
        LBOBINE : "",
        NTOURS : "",
        NINTERRUPT : "",
        OPID : "",
        NPROJET : "",
        NOMBOB : "",
        NUMBOB : "",
        BOBID : "",
        DNOYAU: ""
        }
BOBINE_order = [OPID,
                NPROJET,
                NOMBOB,
                NUMBOB,
                BOBID,
                DFIL,
                LBOBINE,
                DNOYAU,
                NTOURS,
                NINTERRUPT
                ]        

TRANSLATE_BOBINE = {DFIL : "Diamètre du fil (um)",
        LBOBINE : "Longueur de la bobine (mm)",
        NTOURS : "Nombre de tour total",
        NINTERRUPT : "Interruption à ",
        OPID : "Opérateur",
        NPROJET : "Nom du projet",
        NOMBOB : "Type de bobine",
        NUMBOB : "Numéro de la bobine",
        BOBID : "ID bobine",
        DNOYAU: "Diamètre du noyau (mm)"
        }

VARIABLES = {VROT : 0,
            TOUR : 0,
            AVANCEMENT : 0,
            TLEFT : 0,
            TCUMUL : 0,
            TTOTAL : 0,
            RPM : 10,
            AVANCE : 50
            }        

VARIABLES_order = [VROT,
                    TOUR,
                    AVANCEMENT,
                    TLEFT,
                    TCUMUL,
                    TTOTAL,
                    RPM,
                    AVANCE]
TRANSLATE_VARIABLES = {VROT : "vitesse de rotation (RPM)",
                        TOUR : "Nombre de tour effectué",
                        AVANCEMENT : "Avancement (%)",
                        TLEFT : "Temps restant (s)",
                        TCUMUL : "Temps cumulé (s):",
                        TTOTAL : "Temps total (s)",
                        RPM : "Rotation(s) par minutes",
                        AVANCE : "Ecartement entre spires (um)"
                        }
                        