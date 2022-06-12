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
        self.SOC = [] #Liste in der der SOC aller anwesenden Autos gespeichert wird


    def ExtractData(self, car):
        self.EGV = self.CalcEigenverbrauchmitAutoeinspeisung()
        self.plot2 = self.CalcFahrverbrauch(car)
    
    def CalcEigenverbrauch(self, pv, reslast): 
        pv = pv[0:len(reslast)]
        Einspeisung = abs(sum([x for x in reslast if x < 0]))

        Eigenverbrauchsanteil = 1 - Einspeisung/sum(pv)
        Eigenverbrauch = int(sum(pv) * Eigenverbrauchsanteil)# / 1000
        Überschuss = int(sum(pv) - sum(pv) * Eigenverbrauchsanteil)# / 1000
        return Eigenverbrauch, Überschuss

    def CalcFahrverbrauch(self, car):
        discharge = sum(self.resLastDifferenceAfterDischarge)
        charge = sum(self.resLastDifference)
        verlustLaden = charge * (1-car.effizienz)
        vorFahren = charge - verlustLaden

        nachFahren = discharge / car.effizienz
        verlustEntladen = nachFahren * (1-car.effizienz)
        nachFahrenEntladen = nachFahren - verlustEntladen
        verlustGesamt = verlustEntladen + verlustLaden
        Fahrverbrauch = vorFahren - nachFahren
        ret = {"Fahrverbrauch" : Fahrverbrauch,"verlustGesamt" : verlustGesamt
               ,"nachFahrenEntladen" : nachFahrenEntladen}
        return ret


    def CalcEigenverbrauchmitAutoeinspeisung(self):   
        Eigenverbrauch, Überschuss = self.CalcEigenverbrauch(self.PV,self.resLast)
        newResLast = [x + y for (x, y) in zip(self.resLast, self.resLastDifference)]
        EigenverbrauchAfterCharging, ÜberschussAfterCharging = self.CalcEigenverbrauch(self.PV,newResLast)
        ret = {"Eigenverbrauch" : Eigenverbrauch,"Überschuss" : Überschuss
               ,"EigenverbrauchAfterCharging" : EigenverbrauchAfterCharging,"ÜberschussAfterCharging" : ÜberschussAfterCharging}
        return ret


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

        data["01_Eigenverbrauch"] = DS.EGV["Eigenverbrauch"]
        data["01_Überschuss"] = DS.EGV["Überschuss"]
        data["01_EigenverbrauchAfterCharging"] = DS.EGV["EigenverbrauchAfterCharging"]
        data["01_ÜberschussAfterCharging"] = DS.EGV["ÜberschussAfterCharging"]

        data["02_Fahrverbrauch"] = DS.plot2["Fahrverbrauch"]
        data["02_verlustGesamt"] = DS.plot2["verlustGesamt"]
        data["02_nachFahrenEntladen"] = DS.plot2["nachFahrenEntladen"]

        self.scenarioData[scenarioName] = data

    def ExportData(self):

        for key,val in self.scenarioData.items():
            df = pd.DataFrame(val, index= range(1))
            df.to_csv(f"./Ergebnis/Ergebnis_{key}.csv", sep= ";", decimal= ",", encoding= "cp1252")


ScenarioScraper = ScenarioData()