#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def geoliste(g):
    """Fonction pour obtenir la taille et la position de la fenêtre.
    """
    r = [i for i in range(0, len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]), int(g[r[0]+1:r[1]]), int(g[r[1] + 1: r[2]]),
            int(g[r[2] + 1:])]


def addChecksum(bytes_list):
    """Computes the checksum of a list of bytes and appends it
        arguments:
            - bytes_list

        returns [array8_list checksum]
    """
    checksum = 0
    for elem in bytes_list:
        checksum += elem
    checksum = int(checksum % 256)

    return bytes_list.append(checksum)


def convToBytes(integer):
    """Converts an unsigned integer into an array of 4 bytes, in a big-endian
       fashion. Used to send the number of µsteps to the servos.
        arguments :
            - integer : an unsigned integer

        returns [byte[0], byte[1], byte[2], byte[3]]
    """
    _bytes = [0, 0, 0, 0]

    _bytes[0] = integer / (256**3)
    integer = integer % (256**3)
    _bytes[1] = integer / (256**2)
    integer = integer % (256**2)
    _bytes[2] = integer / 256
    integer = integer % 256
    _bytes[3] = integer

    return _bytes
