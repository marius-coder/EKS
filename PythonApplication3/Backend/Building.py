# -*- coding: <latin-1> -*-

import pandas as pd
import matplotlib as plt
import numpy as np

from HL_KL import HL

class Building(HL):
    def __init__(self, wand, dach, boden, fenster, gfa, volumen, anzPersonen, stromVerbrauch):

        self.NFBGF = 0.8 #Verhältnis von Nettofläche zu Bruttogeschoss fläche (max 1)
        self.gfa = gfa #Bruttogeschossfläche in m²
        self.anzPersonen = anzPersonen #Anzahl Personen
        self.heat_capacity = 200 #cp des Gebäudes in Wh/m³
        self.TsWinter = 22 #Solltemperatur im Winter in °C
        self.TsSommer = 26 #Solltemperatur im Sommer in °C
        self.volumen = volumen * 0.8 #Beheiztes Volumen
        self.ABSCHIRMUNGSKOEFF = 0.04 #Abschirmungskoeffizient

        self.ti = 22
        self.cp_air = 0.34  # spez. Wärme kapazität * rho von Luft (Wh/m3K)

        self.stromVerbrauch = stromVerbrauch #Jährlicher Stromverbrauch in kWh/a
        self.WRG = 90 #Wärmerückgewinnung der Lüftung in %
        self.Luftwechsel = 0.5 #Luftwechselrate in n^-1

        self.wand = {"Fläche" : wand["Fläche"],
                     "U-Wert" : wand["U-Wert"],
                     "f_T" : 1}
        self.wand["LT"] = self.calc_LT("wand")

        self.dach = {"Fläche" : dach["Fläche"],
                     "U-Wert": dach["U-Wert"],
                     "f_T": 1}
        self.dach["LT"] = self.calc_LT("dach")

        self.boden = {"Fläche" : boden["Fläche"],
                     "U-Wert": boden["U-Wert"],
                     "f_T": 1}
        self.boden["LT"] = self.calc_LT("boden")

        self.fenster = {"Fläche" : fenster["Fläche"],
                "U-Wert": fenster["U-Wert"],
                "f_T": 1}
        self.fenster["LT"] = self.calc_LT("fenster")

       

    def calc_LT(self, Bauteil:str):
        try:
            return getattr(self, Bauteil)["Fläche"] * getattr(self, Bauteil)["U-Wert"] * getattr(self, Bauteil)["f_T"]

        except:
            return getattr(self, Bauteil)["Fläche"] * getattr(self, Bauteil)["U-Wert"]





#test = Building()
#print(test.calc_QT(-10,20))

#print("")