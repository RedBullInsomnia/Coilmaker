#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def geoliste(g):
    """Fonction pour obtenir la taille et la position de la fenêtre.
    Source: http://python.jpvweb.com/mesrecettespython/doku.php?id=geometrie_fenetre"""
    r=[i for i in range(0,len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]),int(g[r[0]+1:r[1]]),int(g[r[1]+1:r[2]]),int(g[r[2]+1:])]
    
def addChecksum(ARRAY):
    """Fonction qui ajoute la checksum, calculée sur base des bytes de ARRAY
        ARRAY : une liste de bytes
        longARRAY : le nombre de bytes de la liste ARRAY
        
        retourne ARRAY augmenter de la checksum (un byte)
    """
    longARRAY = len(ARRAY)
    #   Les moteurs ont tous l'adresse 0x01.
    #   Le premier byte envoyé au pic est une commande
    #   On remplace donc cette commande par l'adresse : 1
    CKsum = 1
    for x in xrange(1,(longARRAY)):
        CKsum += ARRAY[x]
    CKsum = int(CKsum%256)
    print CKsum
    return ARRAY.append(CKsum)

    
def convertToOctet(entier):
    """Cette fonction transforme un nombre entier > 0 en un tableau de 4 bytes.
    Cette fonction est utilisée pour envoyer le nombre de microstep aux moteurs
    """
    octets = [0,0,0,0]
    octets[0] = entier/(256**3)
    entier = entier%(256**3)
    octets[1] = entier/(256**2)
    entier = entier%(256**2)
    octets[2] = entier/(256**1)
    entier = entier%(256**1)
    octets[3] = entier
    return octets
