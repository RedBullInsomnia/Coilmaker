#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import DEFINE as df
from myThreads import Thread
import os
try:
    import cPickle as pickle
except:
    import pickle


class PdfLatex(Thread):
    """Permet de générer le rapport automatique"""
    def __init__(self, filename, etat, dv, couche):
        Thread.__init__(self, 'LATEX-Gen')
        self.filename = filename
        self.state = etat
        self.dicoBobine = {}
        self.dicoVariables = dv
        self.couche = couche
        try:
            f = open('BOBINE/'+filename+'.bobine', 'r')
        except:
            print("Impossible d'ouvrir le fichier")
            self.logger.error("Impossible d'ouvrir le fichier {}.bobine".
                              format(filename))
        else:
            dicoTmp = pickle.load(f)
            for clef, val in dicoTmp.items():
                self.dicoBobine[clef] = val

    def run(self):
        try:
            f = open('RAPPORT/' + self.filename+'.tex', 'w')
            e = open('RAPPORT/sources/avant.tex', 'r')
            g = open('RAPPORT/sources/apres.tex', 'r')
            eventFile = open('RESULTAT/'+self.filename+'-log-e.csv', 'r')
        except:
            self.l.error("Impossible de créer le fichier {}.tex".format(self.filename))
        else:
            f.write(e.read())
            f.write("\\begin{titlepage}\n")
            f.write("\\begin{center}\n")
            f.write("\\includegraphics[width=0.6\\textwidth]{./sources/microsys.jpg}~ \\\[5cm]\n")
            f.write("\\textsc{\\LARGE Rapport automatique}\\\\[1.5cm]\n")

            if self.state is True:
                f.write("\\textsc{\\Large ECHEC}\\\\[0.5cm]")

            f.write("\\rule{\\linewidth}{0.5mm} \\\\[0.4cm]\n")
            f.write("{ \\huge \\bfseries Bobine \\verb?" +
                    "{}".format(self.dicoBobine[df.BOBID]) +
                    "? \\\\[0.4cm] }\n")
            f.write("\\rule{\\linewidth}{0.5mm} \\\\[3.5cm]\n")
            f.write("\\textsc{\\large \\today}\\\\[0.5cm]\n")
            f.write("\\vfill\n")
            f.write("\\end{center}\n")
            f.write("\\end{titlepage}\n")
            f.write("\\fancyhf{}\n")
            f.write("\\lhead{\\fancyplain{}{Projet: \\verb?" +
                    "{}".format(self.dicoBobine[df.NPROJET]) +
                    "?}} \n")

            if self.state is True:
                f.write("\\chead{\\fancyplain{}{Echec de la bobine}} \n")

            f.write("\\rhead{\\fancyplain{}{Opérateur: \\verb?" +
                    "{}".format(self.dicoBobine[df.OPID]) +
                    "?}}\n")
            f.write("\\lfoot{\\fancyplain{}{\\rightmark}}\n")
            f.write("\\rfoot{\\fancyplain{}{\\thepage}}\n")
            f.write("\\section{Informations sur la bobine}\n")
            f.write("L'opération de bobinage {} avec succès le \\today.\n \n".format(' ne s\'est pas terminé' if self.state else 's\'est terminé'))

            prix = (5.735/1000.0)*3.14*(float(self.dicoBobine[df.LBOBINE]))*(((float(self.dicoBobine[df.DNOYAU])/2.0)+((float(self.dicoBobine[df.DFIL])/1000.0)*(float(self.dicoVariables[df.TOUR])/float(self.dicoBobine[df.LBOBINE]))))**2-(float(self.dicoBobine[df.DNOYAU])/2.0)**2)
            f.write("Le coût en cuivre est estimé à {} euros.\n \n \n".format(round(prix,2)))

            f.write("\\begin{tabular}{ll}\n")
            f.write("Statut de la bobine: & {} \\\\ \n".format('Echec' if self.state else 'Terminé'))
            f.write("Opérateur: & \\verb?{}? \\\\ \n".format(self.dicoBobine[df.OPID]))
            f.write("Nom du projet: & \\verb?{}? \\\\ \n".format(self.dicoBobine[df.NPROJET]))
            f.write("Type de bobine: & \\verb?{}? \\\\ \n".format(self.dicoBobine[df.NOMBOB]))
            f.write("Numéro de la bobine: & \\verb?{}? \\\\ \n".format(self.dicoBobine[df.NUMBOB]))
            f.write("ID bobine: & \\verb?{}? \\\\ \n".format(self.dicoBobine[df.BOBID]))
            f.write("Diamètre du fil: & {} \\\\ \n".format(self.dicoBobine[df.DFIL]+' um'))
            f.write("Diamètre du noyau: & {} \\\\ \n".format(self.dicoBobine[df.DNOYAU]+' mm'))
            f.write("Longueur de la bobine: & {} \\\\ \n".format(self.dicoBobine[df.LBOBINE]+' mm'))
            f.write("Nombre de tours total: & {} spires \\\\ \n".format(round(self.dicoVariables[df.TOUR],2)))
            f.write("Nombre de couches total: & {} couches \\\\ \n".format(int(self.couche)))

            f.write("Temps total: & {} s \\\\ \n".format(round(self.dicoVariables[df.TTOTAL],2)))
            f.write("Temps hors pause: & {} s \\\\ \n".format(round(self.dicoVariables[df.TCUMUL],2)))
            f.write("Interruption à : & {} \\\\ \n".format('Pas d\'interruption' if int(self.dicoBobine[df.NINTERRUPT]) == -1 else self.dicoBobine[df.NINTERRUPT]))
            f.write("\\end{tabular}\n")
            f.write("\clearpage\n")
            f.write("\\section{Vitesse}\n")
            f.write("La vitesse du mandrin est mesurée par le compte-tours. Cette valeur est indicative.\n \n")

            f.write("\\begin{tikzpicture}\n")
            f.write("\\begin{axis}[xlabel = temps écoulé (secondes),ylabel = vitesse de rotation (RPM) ,no markers,legend style={at={(1.02,1)},legend,anchor=north west }]\n")
            f.write("\\addplot table [x=time, y=speed, col sep=semicolon]{{{}.csv}};\n".format(self.filename))
            f.write("\\addplot table [x=time, y=speedC, col sep=semicolon]{{{}.csv}};\n".format(self.filename))
            f.write("\\legend{Mandrin, Consigne}\n")
            f.write("\\end{axis}\n")
            f.write("\\end{tikzpicture}\n")

            f.write("\\section{Avance}\n")
            f.write("Consigne de la vitesse d'avance (en $\mu$m par tour de mandrin)\n \n")
            f.write("\\begin{tikzpicture}\n")
            f.write("\\begin{axis}[xlabel = temps écoulé (secondes),ylabel = avance ($\mu$m/spire) ,no markers,legend style={at={(1.02,1)},legend,anchor=north west }]\n")
            f.write("\\addplot table [x=time, y=avance, col sep=semicolon]{{{}.csv}};\n".format(self.filename))
            f.write("\\legend{avance}\n")
            f.write("\\end{axis}\n")
            f.write("\\end{tikzpicture}\n")

            f.write("\\section{Sonde Hall}\n")

            f.write("\\begin{tikzpicture}\n")
            f.write("\\begin{axis}[xlabel = temps écoulé (secondes),ylabel = Tension (V) ,no markers,legend style={at={(1.02,1)},legend,anchor=north west }]\n")
            f.write("\\addplot table [x=time, y=sondeHall, col sep=semicolon]{{{}.csv}};\n".format(self.filename))
            f.write("\\legend{sondeHall}\n")
            f.write("\\end{axis}\n")
            f.write("\\end{tikzpicture}\n")

            f.write("\\section{Evénements survenus}\n")
            lignes = eventFile.readlines()
            for ligne in lignes:
                f.write(ligne.replace(';', ' - ').replace(':', '\string:')+"\n")
            f.write(g.read())
            f.close()
            e.close()
            g.close()
            os.system("cd RAPPORT ; pdflatex {}.tex; xpdf {}.pdf; cd ..".format(self.filename,self.filename))
        self._stop()
