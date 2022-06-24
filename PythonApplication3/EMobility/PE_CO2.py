# -*- coding: cp1252 -*-
import pandas as pd
from Ladecontroller_Helper import DetermineMonth

class Konversionsfaktoren():

	def __init__(self) -> None:
		#Netzstrom
		self.stromnetzPrimärenergie = {
			"Januar" : 1.8,
			"Februar" : 1.79,
			"März" : 1.72,
			"April" : 1.58,
			"Mai" : 1.47,
			"Juni" : 1.46,
			"Juli" : 1.44,
			"August" : 1.48,
			"September" : 1.58,
			"Oktober" : 1.71,
			"November" : 1.77,
			"Dezember" : 1.79,
			}

		self.stromnetzEmissionen = { #kgCO2/kWh
			"Januar" : 0.304,
			"Februar" : 0.304,
			"März" : 0.264,
			"April" : 0.211,
			"Mai" : 0.167,
			"Juni" : 0.163,
			"Juli" : 0.163,
			"August" : 0.167,
			"September" : 0.208,
			"Oktober" : 0.260,
			"November" : 0.282,
			"Dezember" : 0.291,
			}
		self.fernwärmePrimärenergie = 1.6
		self.fernwärmeEmissionen = 59 #kgCO2/kWh

		


	def CalcPE(self, szen, name, gfa, resLast = None):
		buildings = {"W1":15.35,"W2":15.99,"W3":16.33,"W4":14.19,"G1":3.07,"G2":3.9,"G3":4.98,"G4":2.87,"S1":17.98,"S2":5.35}
		#szens = ["FW","WP"]

		df = pd.read_csv(f"./Ergebnis/Ergebnis_Gebäude{szen}.csv", delimiter= ";", decimal= ",", encoding= "cp1252")
		for building, percent in buildings.items():
			interPE = []
			interCO2 = []
			for hour in range(8760):
				if szen == "WP":
					if resLast == None:
						strombedarf = df[building+"_stromBedarf [kWh]"][hour]
					else:
						strombedarf = (resLast[hour] / gfa) * percent / 100
					interPE.append(strombedarf * list(self.stromnetzPrimärenergie.values())[DetermineMonth(hour)-1])
					interCO2.append(strombedarf * list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1])
				if szen == "FW":
					if resLast == None:
						strombedarf = df[building+"_stromBedarf [kWh]"][hour]
					else:
						strombedarf = (resLast[hour] / gfa) * percent / 100
					interPE.append(strombedarf * list(self.stromnetzPrimärenergie.values())[DetermineMonth(hour)-1])
					interCO2.append(strombedarf * list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1])
			df[f"{building}_Primärenergie_{name} [kWh/m²]"]= interPE
			df[f"{building}_CO2_{name} [kgCO2/m²]"]= interCO2
		df.to_csv(f"./Ergebnis/Ergebnis_Gebäude"+szen+".csv", sep= ";", decimal= ",", encoding= "cp1252")
PE_CO2 = Konversionsfaktoren()
	



