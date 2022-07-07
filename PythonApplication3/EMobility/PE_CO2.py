# -*- coding: cp1252 -*-
import pandas as pd
from Ladecontroller_Helper import DetermineMonth

class Konversionsfaktoren():

	def __init__(self) -> None:
		#Netzstrom
		self.stromnetzPrim�renergie = {
			"Januar" : 1.8,
			"Februar" : 1.79,
			"M�rz" : 1.72,
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
			"M�rz" : 0.264,
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
		self.fernw�rmePrim�renergie = 1.6
		self.fernw�rmeEmissionen = 0.059 #kgCO2/kWh


	def CalcEnergiefl�sse(self, obj, geb�udeLast, externeLadung=0, emobilit�tPVCharging=0 ,pv=0, emobilit�tGridCharging= 0,
					  emobilit�tZureisende=0,Emobilit�tzuGeb�udeErneuerbar=0, Emobilit�tzuGeb�udeNetz=0,
					  fahrverbrauchLokal=0,fahrverbrauchNetz=0):
		PVtoGeb�ude = min(pv,geb�udeLast)
		
		PVtoEmobilit�t = emobilit�tPVCharging

		PVtoZureisende = emobilit�tZureisende

		PVtoNetz = max(0,pv-(PVtoGeb�ude+PVtoZureisende+PVtoEmobilit�t))

		ExterntoEmobilit�t = externeLadung
		NetztoEmobilit�t = emobilit�tGridCharging

		#Emobilit�tzuGeb�udeErneuerbar = Emobilit�tzuGeb�udeErneuerbar
		#Emobilit�tzuGeb�udeNetz = Emobilit�tzuGeb�udeNetz

		NetztoGeb�ude = geb�udeLast - (PVtoGeb�ude + Emobilit�tzuGeb�udeErneuerbar + Emobilit�tzuGeb�udeNetz)


		Netz = NetztoGeb�ude + ExterntoEmobilit�t + NetztoEmobilit�t 
		Erneuerbar = PVtoGeb�ude
		Gutschreibung = PVtoZureisende + PVtoNetz

		obj["Netz"].append(Netz)
		obj["Erneuerbar"].append(Erneuerbar)
		obj["Gutschreibung"].append(Gutschreibung)

	def CalcPrim�rEnergie(self, data, hour, gfa):
		pe = 0
		pe += data["Netz"][hour] * list(self.stromnetzPrim�renergie.values())[DetermineMonth(hour)-1] / gfa
		pe += data["Erneuerbar"][hour] / gfa
		pe += data["Gutschreibung"][hour] * list(self.stromnetzPrim�renergie.values())[DetermineMonth(hour)-1] *-1 / gfa

		return pe

	def CalcCO2(self, data, hour, gfa):
		co2 = 0
		co2 += data["Netz"][hour] * list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1] / gfa
		co2 += data["Erneuerbar"][hour] * 0.045 / gfa
		co2 += data["Gutschreibung"][hour] * (list(self.stromnetzEmissionen.values())[DetermineMonth(hour)-1]) *-1 / gfa

		return co2

		

	def CalcPE(self, szen,szenPV, name, gfa, pvChargingHourly, gridChargingHourly, resLast = None):
		df= pd.DataFrame()
		primEnergieOhnePV = self.CalcEnergiefl�sse()
		

		df[f"Prim�renergie_{name[0]} [kWh/m�]"]= primEnergieOhnePV
		df[f"Prim�renergie_{name[1]} [kWh/m�]"]= primEnergieMitPV
		df[f"Prim�renergie_{name[2]} [kWh/m�]"]= primEnergieMitPVMitLC
		df[f"Prim�renergie_{name[3]} [kWh/m�]"]= primEnergieMitPVMitZureisende
		df.to_csv(f"./Ergebnis/Endergebnis/Ergebnis_Geb�ude_{szenPV}_{szen}.csv", sep= ";", decimal= ",", encoding= "cp1252")


		
PE_CO2 = Konversionsfaktoren()
	



