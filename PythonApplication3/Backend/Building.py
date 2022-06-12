# -*- coding: <latin-1> -*-

import pandas as pd
import matplotlib as plt
import numpy as np

from HL_KL import HL
from Dataflows import Dataflows
from Warmwasser import WW

class Building(HL,Dataflows,WW):
    def __init__(self, wand, dach, boden, fenster, gfa, volumen, anzPersonen, stromVerbrauch):
        WW.__init__(self)
        self.DF = Dataflows()
        self.NFBGF = 0.8 #Verhältnis von Nettofläche zu Bruttogeschoss fläche (max 1)
        self.gfa = gfa #Bruttogeschossfläche in m²
        self.anzPersonen = anzPersonen #Anzahl Personen
        self.heat_capacity = 150 #cp des Gebäudes in Wh/m³
        self.TsWinter = 20 #Solltemperatur im Winter in °C
        self.TsSommer = 26 #Solltemperatur im Sommer in °C
        self.volumen = volumen * 0.8 #Beheiztes Volumen
        self.ABSCHIRMUNGSKOEFF = 0.04 #Abschirmungskoeffizient
        self.Warmebrucken = 0.05        

        self.ti = 20 #°C
        self.cp_air = 0.34  # spez. Wärme kapazität * rho von Luft (Wh/m3K)

        self.stromVerbrauch = stromVerbrauch #Jährlicher Stromverbrauch in kWh/a
        self.stromVerbrauchBetrieb = 0
        self.WRG = 75 #Wärmerückgewinnung der Lüftung in %
        self.Luftwechsel = 1 #Luftwechselrate in n^-1

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
            return getattr(self, Bauteil)["Fläche"] * (getattr(self, Bauteil)["U-Wert"]+self.Warmebrucken) * getattr(self, Bauteil)["f_T"]

        except:
            return getattr(self, Bauteil)["Fläche"] * getattr(self, Bauteil)["U-Wert"]

    def AddDataflows(self, qHL):

        self.DF.qHL.append(qHL)
        self.DF.qWW.append(0)
        self.DF.stromBedarf.append(self.stromVerbrauchBetrieb)
        self.DF.tInnen.append(self.ti)

        if self.DF.szen == "WP":
            self.DF.stromWP_HZG.append(self.WP_HZG.PelBetrieb)
            self.DF.qWP_HZG.append(self.WP_HZG.PelBetrieb * self.WP_HZG.COP_HZG)
            #self.DF.stromWP_WW.append(self.WP_WW.PelBetrieb)
            #self.DF.qWP_WW.append(self.WP_WW.PelBetrieb * self.WP_WW.COP_HZG)




#test = Building()
#print(test.calc_QT(-10,20))

#print("")