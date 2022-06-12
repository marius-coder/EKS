# -*- coding: cp1252 -*-
import dataclasses as dataclass
import seaborn as sns
import matplotlib.pyplot as plt
import bokeh
import pandas as pd

class DataScraper():

    def __init__(self) -> None:
        self.Init_eMobility()

        

    def Init_eMobility(self):
        self.li_state = []			#Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)
        self.li_stateCars = []		#Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)
        self.useableCapacity = []	#Liste in der die verwendbare Kapazitat gespeichert wird zum plotten
        self.demandBuilding = []	#Liste in der der Bedarf des Gebäudes gespeichert wird
        self.demandDriving = []		#Liste in der der Bedarf der Autos zum Fahren gespeichert wird
        self.demandcovered = []		#Liste in der der Bedarf der durch die E-Autos gedeckt wird gespeichert wird
        self.PV = []		        #Liste in der die von auserhalb produzierte Leistung gespeichert wird
        self.generationloaded = []  #Liste die speichert, wie viel Energie in den Autos gespeichert wurde
        self.resLast = []           #Liste in der die Residuallast gespeichert wird
        self.demandDriven = 0       #Variable in der die zum Fahren verbrauchte Energie hochsummiert wird
        self.gridCharging = 0       #Variable in der die zum Fahren aus dem Netz bezogene Energie hochsummiert wird

        self.resLastDifferenceAfterDischarge = [0] * 8760
        self.resLastDifference = [0] * 8760
        self.resLastAfterDischarging = [0] * 8760
        self.resLastAfterCharging = [0] * 8760
        self.SOC = [] #Liste in der der SOC aller anwesenden Autos gepsiechert wird


Scraper = DataScraper()


#@dataclass
#class ScenarioData:
#    demandDriven = 0         
#    gridCharging = 0
#    energyPvToCar = 0
#    CarToBuilding = 0
#    Pv = 0
#    demandBuilding = 0

class ScenarioData:
    def __init__(self) -> None:
        self.scenarioData = {}



    def AppendData(self, DS, scenarioName: str):
        data = {}

        data["demandDriven"] = DS.demandDriven
        data["gridCharging"] = DS.gridCharging
        data["energyPvToCar"] = sum(DS.resLastDifference)
        data["CarToBuilding"] = sum(DS.resLastDifferenceAfterDischarge)
        data["Pv"] = sum(DS.PV)
        data["demandBuilding"] = sum(DS.demandBuilding)
        data["Residuallast"] = sum(DS.resLast)

        self.scenarioData[scenarioName] = data

ScenarioScraper = ScenarioData()