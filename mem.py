#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class Mem:
    def __init__(self):
        self.CT = False
        self.core = False
        self.SH = False
        self.pos = False

    def setCT(self, CT):
        self.CT = CT

    def setCore(self, core):
        self.core = core

    def setSH(self, sh):
        self.SH = sh

    def setPos(self, pos):
        self.pos = pos
