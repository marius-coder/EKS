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
		self.fernwärmeEmissionen = 0.059 #kgCO2/kWh


	def CalcEnergieflüsse(self, obj, gebäudeLast, externeLadung=0, emobilitätPVCharging=0 ,pv=0, emobilitätGridCharging= 0,
					  emobilitätZureisende=0,EmobilitätzuGebäudeErneuerbar=0, EmobilitätzuGebäudeNetz=0,
					  fahrverbrauchLokal=0,fahrverbrauchNetz=0):
		PVtoGebäude = min(pv,gebäudeLast)
		
		PVtoEmobilität = emobilitätPVCharging

		PVtoZureisende = emobilitätZureisende

		PVtoNetz = max(0,pv-(PVtoGebäude+PVtoZureisende+PVtoEmobilität))

		ExterntoEmobilität = externeLadung
		NetztoEmobilität = emobilitätGridCharging

		#EmobilitätzuGebäudeErneuerbar = EmobilitätzuGebäudeErneuerbar
		#EmobilitätzuGebäudeNetz = EmobilitätzuGebäudeNetz

		NetztoGebäude = gebäudeLast - (PVtoGebäude + EmobilitätzuGebäudeErneuerbar + EmobilitätzuGebäudeNetz)


		Netz = NetztoGebäude + ExterntoEmobilität + NetztoEmobilität 
		Erneuerbar = PVtoGebäude
		Gutschreibung = PVtoZureisende + PVtoNetz

		obj["Netz"].append(Netz)
		obj["Erneuerbar"].append(Erneuerbar)
		obj["Gutschreibung"].append(Gutschreibung)

	def CalcPrimärEnergie(self, data, hour, gfa):
		pe = 0
		pe += data["Netz"][hour] * list(self.stromnetzPrimärenergie.values())[DetermineMonth(hour)-1] / gfa
		pe += data["Erneuerbar"][hour] / gfa
		pe += data["Gutschreibung"][hour] * list(self.stromnetzPrimärenergie.values())[DetermineMonth(hour)-1] *-1 / gfa

		return pe

	def CalcCO2(self, data, hour, gfa):
		co2 = 0
		co2 += data["Netz"][hour] * list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1] / gfa
		co2 += data["Erneuerbar"][hour] * 0.045 / gfa
		co2 += data["Gutschreibung"][hour] * (list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1]) *-1 / gfa

		return co2

		

	def CalcPE(self, szen,szenPV, name, gfa, pvChargingHourly, gridChargingHourly, resLast = None):
		df= pd.DataFrame()
		primEnergieOhnePV = self.CalcEnergieflüsse()
		

		df[f"Primärenergie_{name[0]} [kWh/m²]"]= primEnergieOhnePV
		df[f"Primärenergie_{name[1]} [kWh/m²]"]= primEnergieMitPV
		df[f"Primärenergie_{name[2]} [kWh/m²]"]= primEnergieMitPVMitLC
		df[f"Primärenergie_{name[3]} [kWh/m²]"]= primEnergieMitPVMitZureisende
		df.to_csv(f"./Ergebnis/Endergebnis/Ergebnis_Gebäude_{szenPV}_{szen}.csv", sep= ";", decimal= ",", encoding= "cp1252")


		
PE_CO2 = Konversionsfaktoren()
	



