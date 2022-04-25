# -*- coding: <latin-1> -*-

import pandas as pd
import matplotlib as plt
import numpy as np

from HL_KL import HL

class Building(HL):
    def __init__(self):

        self.NFBGF = 1 #Verhältnis von Nettofläche zu Bruttogeschoss fläche (max 1)
        self.gfa = 1 #Bruttogeschossfläche in m²
        self.heat_capacity = 200 #cp des Gebäudes in Wh/m³
        self.net_storey_height = 2.8 #Geschosshöhe in m
        self.TsWinter = 22 #Solltemperatur im Winter in °C
        self.TsSommer = 26 #Solltemperatur im Sommer in °C
        self.volumen = self.gfa * self.net_storey_height * 0.8 #Beheiztes Volumen
        self.ABSCHIRMUNGSKOEFF = 0.04 #Abschirmungskoeffizient


        self.WRG = 95 #Wärmerückgewinnung der Lüftung in %
        self.Luftwechsel = 1 #Luftwechselrate in n^-1

        self.wand = {"Fläche" : 1,
                     "U-Wert" : 1,
                     "f_T" : 1,}
        self.wand["LT"] = self.calc_LT("wand")

        self.dach = {"Fläche" : 2,
                     "U-Wert": 2,
                     "f_T": 2}
        self.dach["LT"] = self.calc_LT("dach")

        self.fußboden = {"Fläche" : 3,
                     "U-Wert": 3,
                     "f_T": 3}
        self.fußboden["LT"] = self.calc_LT("fußboden")

        self.window = {"Fläche" : 4,
                "U-Wert": 4,
                "f_T": 4}
        self.window["LT"] = self.calc_LT("window")

       

    def calc_LT(self, Bauteil:str):
        try:
            return getattr(self, Bauteil)["Fläche"] * getattr(self, Bauteil)["U-Wert"] * getattr(self, Bauteil)["f_T"]

        except:
            return getattr(self, Bauteil)["Fläche"] * getattr(self, Bauteil)["U-Wert"]





test = Building()
print(test.calc_QT(-10,20))

print("")