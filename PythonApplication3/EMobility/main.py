# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus, PlotVerteilungen, PlotEinflussLDC

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows

from ReadInput import inputData

from PE_CO2 import PE_CO2

import Plotting.DataScraper as DS

import numpy as np
import pandas as pd

AutoDaten = inputData["AutoDaten"]
PersonenDaten = inputData["PersonenDaten"]
ExterneDaten = inputData["ExterneDaten"]
LadeDaten = inputData["LadeDaten"]["distMinLadung"]

scenarios = ["PV", "PV_max"]
dataW�rme = [Strombedarf["FW"],Strombedarf["WP"]]
scenariosW�rme = ["FW","WP"]


def GetPVOnly(scen):
	DS.scraper.__init__()
	DS.ZV.__init__()
	DS.zeitVar.__init__()
	PVOnly = LadeController(AutoDaten= AutoDaten, distMinLadung= {"100":100}, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
	PV = DefinePV(scen)
	for hour in range(8760):
		pv = PV[hour]
		bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + scenW�rme[hour]

		resLast = bedarf - pv
		DS.zeitVar.resLastBeforeEMobility[hour] = resLast
		PVOnly.CheckTimestep(hour= hour,resLast= resLast)
		LadeZyklen = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / PVOnly.anzAutos
	return DS.zeitVar.gridChargingHourly, DS.zeitVar.pvChargingHourly, DS.zeitVar.fahrverbrauchNetz, DS.zeitVar.fahrverbrauchLokal, LadeZyklen


df_PE_CO2 = pd.DataFrame()

for scen in scenarios:
	for i, scenW�rme in enumerate(dataW�rme):
		PVDaten = GetPVOnly(scen)
		DS.scraper.__init__()
		DS.ZV.__init__()
		DS.zeitVar.__init__()
		Control = LadeController(AutoDaten= AutoDaten, distMinLadung= LadeDaten, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
		PV = DefinePV(scen)

		gesamtBedarf = [a + b + c + d for a,b,c,d in zip(Strombedarf["Wohnen"], Strombedarf["Gewerbe"],Strombedarf["Schule"],scenW�rme)]
		primEnergieOhnePV={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitPV={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitLC={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitZureisende={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		listPE = [primEnergieOhnePV,primEnergieMitPV,primEnergieMitLC,primEnergieMitZureisende]
		listCO2 = []

		dict_PE_CO2= {"PE_OhnePV [kWh/m�]":[],"CO2_OhnePV [kg/m�]":[],"PE_MitPV [kWh/m�]":[],"CO2_MitPV [kg/m�]":[],
						"PE_MitLC [kWh/m�]":[],"CO2_MitLC [kg/m�]":[],"PE_MitZureisende [kWh/m�]":[],"CO2_MitZureisende [kg/m�]":[]}
		



		for hour in range(8760):
			pv = PV[hour]
			bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + scenW�rme[hour]

			#resLast = 1 - pv
			resLast = bedarf - pv
			DS.zeitVar.resLastBeforeEMobility[hour] = resLast
			Control.CheckTimestep(hour= hour,resLast= resLast)
			
			PE_CO2.CalcEnergiefl�sse(obj= primEnergieOhnePV, geb�udeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour]+ DS.zeitVar.fahrverbrauchLokal[hour],
												externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour])
			 
			PE_CO2.CalcEnergiefl�sse(obj= primEnergieMitPV,geb�udeLast= bedarf,fahrverbrauchNetz= PVDaten[2][hour],
									externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, fahrverbrauchLokal= PVDaten[3][hour]
									)

			PE_CO2.CalcEnergiefl�sse(obj= primEnergieMitLC,geb�udeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour], emobilit�tGridCharging= DS.zeitVar.gridChargingHourly[hour],
							externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, Emobilit�tzuGeb�udeErneuerbar= DS.zeitVar.entladungLokal[hour],
							fahrverbrauchLokal= DS.zeitVar.fahrverbrauchLokal[hour],Emobilit�tzuGeb�udeNetz= DS.zeitVar.entladungNetz[hour])

			PE_CO2.CalcEnergiefl�sse(obj= primEnergieMitZureisende,geb�udeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour],
							externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, emobilit�tGridCharging= DS.zeitVar.gridChargingHourly[hour],
							fahrverbrauchLokal= DS.zeitVar.fahrverbrauchLokal[hour],emobilit�tZureisende= DS.zeitVar.LadeLeistungAu�enstehende[hour])
			names = ["OhnePV","MitPV","MitLC","MitZureisende"]
			liste = []
			for dic,name in zip(listPE,names):
				pe = PE_CO2.CalcPrim�rEnergie(data= dic, hour= hour, gfa= Control.gfa)
				co2 = PE_CO2.CalcCO2(data= dic, hour= hour, gfa= Control.gfa)
				dict_PE_CO2[f"PE_{name} [kWh/m�]"].append(pe)
				dict_PE_CO2[f"CO2_{name} [kg/m�]"].append(co2)
		df_PE_CO2 = pd.DataFrame(dict_PE_CO2)
		df_PE_CO2.to_csv(f"./Ergebnis/Endergebnis/Ergebnis_Geb�ude_{scen}_{scenariosW�rme[i]}.csv", sep= ";", decimal= ",", encoding= "cp1252")
		personenKilometerElektrisch = 0
		for person in Control.persons:
			personenKilometerElektrisch += person.wegMitAuto 
		print(personenKilometerElektrisch / len(Control.persons))
		#Personenkilometer
		DS.scraper.generell["personenKilometer Elektrisch durch. [km]"] = personenKilometerElektrisch / len(Control.persons)
		DS.scraper.generell["personenKilometer Elektrisch [km]"] = personenKilometerElektrisch
		DS.scraper.generell["personenKilometer Fossil [km]"] = Control.anzPersonen * Control.personenKilometer - personenKilometerElektrisch

		#Stromverbrauch
		DS.scraper.generell["stromverbrauch Wohnen [kWh/m�]"] = sum(Strombedarf["Wohnen"]) / Control.gfa
		DS.scraper.generell["stromverbrauch Gewerbe [kWh/m�]"] = sum(Strombedarf["Gewerbe"]) / Control.gfa
		DS.scraper.generell["stromverbrauch Schule [kWh/m�]"] = sum(Strombedarf["Schule"]) / Control.gfa
		DS.scraper.generell["stromverbrauch WP [kWh/m�]"] = sum(Strombedarf["WP"]) / Control.gfa
		DS.scraper.generell["stromverbrauch E-Mobilit�t [kWh/Auto]"] = DS.ZV.verbrauchFahrenEmobilit�t / Control.anzAutos

		#PV
		DS.scraper.generell["pvProduktion [kWh]"] = sum(PV)
		DS.scraper.generell["pvProduktionGfa [kWh/m�]"] = sum(PV) / Control.gfa

		#Indikatoren
		DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] = DS.ZV.fehlgeschlageneFahrversuche / DS.ZV.fahrversuche * 100
		DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilit�t [%/Auto]"] = np.mean(DS.zeitVar.ungenutzteLadung) / Control.anzAutos
		DS.scraper.indikatoren["erh�hung Eigenverbrauch E-Mobilit�t [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["erh�hung Eigenverbrauch Zureisende [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto [Anzahl]"] = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto ohne LC [Anzahl]"] = PVDaten[4]
		DS.scraper.indikatoren["Reserveautos [Anzahl]"] = sum(DS.zeitVar.anzahlReserveAutos) / len(DS.zeitVar.anzahlReserveAutos)
		

		#Verbrauch der E-Mobilit�t zum Fahren
		DS.scraper.eMobilit�tFahren["Gesamt [kWh/Auto]"] = DS.ZV.verbrauchFahrenEmobilit�t / Control.anzAutos
		DS.scraper.eMobilit�tFahren["Lokal [kWh/Auto]"] = sum(DS.zeitVar.fahrverbrauchLokal) / Control.anzAutos
		DS.scraper.eMobilit�tFahren["Netz [kWh/Auto]"] = sum(DS.zeitVar.fahrverbrauchNetz) / Control.anzAutos
		DS.scraper.eMobilit�tFahren["externe Ladung [kWh/Auto]"] = sum(DS.zeitVar.LadeLeistungExterneStationen) / Control.anzAutos

		#Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
		daten = CalcEMobilityBuildingEnergyFlows(discharge= sum(DS.zeitVar.eMobilityDischarge), charge= sum(DS.zeitVar.eMobilityCharge),
										  car= Control.li_Autos[0],externCharge= sum(DS.zeitVar.LadeLeistungExterneStationen))
		DS.scraper.eMobilit�tGeb�ude["EMobilit�tzuGeb�ude [kWh/Auto]"] = daten[0] * Control.li_Autos[0].effizienz / Control.anzAutos
		DS.scraper.eMobilit�tGeb�ude["Fahrverbrauch [kWh/Auto]"] = daten[1] / Control.anzAutos
		DS.scraper.eMobilit�tGeb�ude["Lade/Entladeverluste [kWh/Auto]"] = daten[2] / Control.anzAutos
		DS.scraper.eMobilit�tGeb�ude["Geb�udezuEMobilit�t [kWh/Auto]"] = sum(DS.zeitVar.eMobilityCharge) * Control.li_Autos[0].effizienz / Control.anzAutos
		DS.scraper.eMobilit�tGeb�ude["EMobilit�tzuGeb�ude [kWh/m�]"] = daten[0] * Control.li_Autos[0].effizienz / Control.gfa
		DS.scraper.eMobilit�tGeb�ude["Lade/Entladeverluste [kWh/m�]"] = daten[2] / Control.gfa
		DS.scraper.eMobilit�tGeb�ude["Geb�udezuEMobilit�t [kWh/m�]"] = sum(DS.zeitVar.eMobilityCharge) * Control.li_Autos[0].effizienz / Control.gfa
	
		#PV-Daten vor E-Mobilit�t
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)
		DS.scraper.pvVorEMobilit�t["Eigenverbrauch [kWh/m�]"] = daten[0] / Control.gfa
		DS.scraper.pvVorEMobilit�t["Einspeisung [kWh/m�]"] = daten[1] / Control.gfa
		DS.scraper.pvVorEMobilit�t["Netzbezug [kWh/m�]"] = abs(sum([x for x in DS.zeitVar.resLastBeforeEMobility if x > 0])) / Control.gfa
		
		#PV-Daten nach E-Mobilit�t
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)
		DS.scraper.pvNachEMobilit�t["Eigenverbrauch [kWh/m�]"] = daten[0] / Control.gfa
		DS.scraper.pvNachEMobilit�t["Einspeisung [kWh/m�]"] = daten[1] / Control.gfa
		DS.scraper.pvNachEMobilit�t["Netzbezug [kWh/m�]"] = abs(sum([x for x in DS.zeitVar.resLastAfterEMobility if x > 0])) / Control.gfa

		#PV-Daten nach Zureisenden
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)
		DS.scraper.pvNachZureisenden["Eigenverbrauch [kWh/m�]"] = daten[0] / Control.gfa
		DS.scraper.pvNachZureisenden["Einspeisung [kWh/m�]"] = daten[1] / Control.gfa
		DS.scraper.pvNachZureisenden["Netzbezug [kWh/m�]"] = abs(sum([x for x in DS.zeitVar.resLastAfterZureisende if x > 0])) / Control.gfa
		DS.scraper.zureisenden["Ladung [kWh/m�]"] = sum(DS.zeitVar.LadeLeistungAu�enstehende) / Control.gfa	

		#Prim�renergie
		PE_Fossil = Control.anzPers*(1-Control.percent)*80/100*personenKilometerElektrisch*1.2 / Control.gfa
		if scenariosW�rme[i] == "FW":
			PE_FW = abs(sum(pd.read_csv("./Ergebnis/Strombedarf_FW.csv", decimal=",", sep=";", encoding= "cp1252")["W�rmebedarf_FW"].tolist()) / Control.gfa * PE_CO2.fernw�rmePrim�renergie)
		else:
			PE_FW = 0
		DS.scraper.prim�renergie["PE_OhnePV [kWh/m�]"] = sum(dict_PE_CO2["PE_OhnePV [kWh/m�]"]) + PE_Fossil + PE_FW
		DS.scraper.prim�renergie["PE_MitPV [kWh/m�]"] = sum(dict_PE_CO2["PE_MitPV [kWh/m�]"]) + PE_Fossil + PE_FW
		DS.scraper.prim�renergie["PE_MitEmobilit�t [kWh/m�]"] = sum(dict_PE_CO2["PE_MitLC [kWh/m�]"]) + PE_Fossil + PE_FW

		#CO2-Emissionen
		CO2_Fossil = PE_Fossil * 0.250
		CO2_FW = PE_FW * PE_CO2.fernw�rmeEmissionen
		DS.scraper.CO2Emissionen["CO2_OhnePV [kg/m�]"] = sum(dict_PE_CO2["CO2_OhnePV [kg/m�]"]) + CO2_Fossil + CO2_FW
		DS.scraper.CO2Emissionen["CO2_MitPV [kg/m�]"] = sum(dict_PE_CO2["CO2_MitPV [kg/m�]"]) + CO2_Fossil + CO2_FW
		DS.scraper.CO2Emissionen["CO2_MitEmobilit�t [kg/m�]"] = sum(dict_PE_CO2["CO2_MitLC [kg/m�]"]) + CO2_Fossil + CO2_FW

		#Export Data
		DS.scraper.Export(f"{scen}_{scenariosW�rme[i]}")	

		DS.zeitVar.Export(f"{scen}_{scenariosW�rme[i]}")


		if scenariosW�rme[i] == "WP" and scen == "PV":
			pass
			#PlotStatusCollection(DS.zeitVar.StateofCars)
			#PlotPersonStatus(DS.zeitVar.StateofDrivingPersons)
			#PlotEinflussLDC(gesamtBedarf, PV, DS.zeitVar.entladungLokal, DS.zeitVar.pvChargingHourly) #DS.zeitVar.pvChargingHourly
			#PlotVerteilungen(DS.zeitVar.eMobilityCharge, "Ladeleistung")
			#PlotVerteilungen(DS.zeitVar.eMobilityDischarge, "EntladeLeistung")
			#PlotVerteilungen(DS.zeitVar.LadeLeistungAu�enstehende, "LadeLeistung Zureisende")
			#PlotVerteilungen(gesamtBedarf, "Geb�udebedarf")


		
		##PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)

	


