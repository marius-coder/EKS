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
dataWärme = [Strombedarf["FW"],Strombedarf["WP"]]
scenariosWärme = ["FW","WP"]


def GetPVOnly(scen):
	DS.scraper.__init__()
	DS.ZV.__init__()
	DS.zeitVar.__init__()
	PVOnly = LadeController(AutoDaten= AutoDaten, distMinLadung= {"100":100}, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
	PV = DefinePV(scen)
	for hour in range(8760):
		pv = PV[hour]
		bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + scenWärme[hour]

		resLast = bedarf - pv
		DS.zeitVar.resLastBeforeEMobility[hour] = resLast
		PVOnly.CheckTimestep(hour= hour,resLast= resLast)
		LadeZyklen = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / PVOnly.anzAutos
	return DS.zeitVar.gridChargingHourly, DS.zeitVar.pvChargingHourly, DS.zeitVar.fahrverbrauchNetz, DS.zeitVar.fahrverbrauchLokal, LadeZyklen


df_PE_CO2 = pd.DataFrame()

for scen in scenarios:
	for i, scenWärme in enumerate(dataWärme):
		PVDaten = GetPVOnly(scen)
		DS.scraper.__init__()
		DS.ZV.__init__()
		DS.zeitVar.__init__()
		Control = LadeController(AutoDaten= AutoDaten, distMinLadung= LadeDaten, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
		PV = DefinePV(scen)

		gesamtBedarf = [a + b + c + d for a,b,c,d in zip(Strombedarf["Wohnen"], Strombedarf["Gewerbe"],Strombedarf["Schule"],scenWärme)]
		primEnergieOhnePV={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitPV={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitLC={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		primEnergieMitZureisende={"Netz":[],"Erneuerbar":[],"Gutschreibung":[]}
		listPE = [primEnergieOhnePV,primEnergieMitPV,primEnergieMitLC,primEnergieMitZureisende]
		listCO2 = []

		dict_PE_CO2= {"PE_OhnePV [kWh/m²]":[],"CO2_OhnePV [kg/m²]":[],"PE_MitPV [kWh/m²]":[],"CO2_MitPV [kg/m²]":[],
						"PE_MitLC [kWh/m²]":[],"CO2_MitLC [kg/m²]":[],"PE_MitZureisende [kWh/m²]":[],"CO2_MitZureisende [kg/m²]":[]}
		



		for hour in range(8760):
			pv = PV[hour]
			bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + scenWärme[hour]

			#resLast = 1 - pv
			resLast = bedarf - pv
			DS.zeitVar.resLastBeforeEMobility[hour] = resLast
			Control.CheckTimestep(hour= hour,resLast= resLast)
			
			PE_CO2.CalcEnergieflüsse(obj= primEnergieOhnePV, gebäudeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour]+ DS.zeitVar.fahrverbrauchLokal[hour],
												externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour])
			 
			PE_CO2.CalcEnergieflüsse(obj= primEnergieMitPV,gebäudeLast= bedarf,fahrverbrauchNetz= PVDaten[2][hour],
									externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, fahrverbrauchLokal= PVDaten[3][hour]
									)

			PE_CO2.CalcEnergieflüsse(obj= primEnergieMitLC,gebäudeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour], emobilitätGridCharging= DS.zeitVar.gridChargingHourly[hour],
							externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, EmobilitätzuGebäudeErneuerbar= DS.zeitVar.entladungLokal[hour],
							fahrverbrauchLokal= DS.zeitVar.fahrverbrauchLokal[hour],EmobilitätzuGebäudeNetz= DS.zeitVar.entladungNetz[hour])

			PE_CO2.CalcEnergieflüsse(obj= primEnergieMitZureisende,gebäudeLast= bedarf,fahrverbrauchNetz= DS.zeitVar.fahrverbrauchNetz[hour],
							externeLadung= DS.zeitVar.LadeLeistungExterneStationen[hour], pv= pv, emobilitätGridCharging= DS.zeitVar.gridChargingHourly[hour],
							fahrverbrauchLokal= DS.zeitVar.fahrverbrauchLokal[hour],emobilitätZureisende= DS.zeitVar.LadeLeistungAußenstehende[hour])
			names = ["OhnePV","MitPV","MitLC","MitZureisende"]
			liste = []
			for dic,name in zip(listPE,names):
				pe = PE_CO2.CalcPrimärEnergie(data= dic, hour= hour, gfa= Control.gfa)
				co2 = PE_CO2.CalcCO2(data= dic, hour= hour, gfa= Control.gfa)
				dict_PE_CO2[f"PE_{name} [kWh/m²]"].append(pe)
				dict_PE_CO2[f"CO2_{name} [kg/m²]"].append(co2)
		df_PE_CO2 = pd.DataFrame(dict_PE_CO2)
		df_PE_CO2.to_csv(f"./Ergebnis/Endergebnis/Ergebnis_Gebäude_{scen}_{scenariosWärme[i]}.csv", sep= ";", decimal= ",", encoding= "cp1252")
		personenKilometerElektrisch = 0
		for person in Control.persons:
			personenKilometerElektrisch += person.wegMitAuto 
		print(personenKilometerElektrisch / len(Control.persons))
		#Personenkilometer
		DS.scraper.generell["personenKilometer Elektrisch durch. [km]"] = personenKilometerElektrisch / len(Control.persons)
		DS.scraper.generell["personenKilometer Elektrisch [km]"] = personenKilometerElektrisch
		DS.scraper.generell["personenKilometer Fossil [km]"] = Control.anzPersonen * Control.personenKilometer - personenKilometerElektrisch

		#Stromverbrauch
		DS.scraper.generell["stromverbrauch Wohnen [kWh/m²]"] = sum(Strombedarf["Wohnen"]) / Control.gfa
		DS.scraper.generell["stromverbrauch Gewerbe [kWh/m²]"] = sum(Strombedarf["Gewerbe"]) / Control.gfa
		DS.scraper.generell["stromverbrauch Schule [kWh/m²]"] = sum(Strombedarf["Schule"]) / Control.gfa
		DS.scraper.generell["stromverbrauch WP [kWh/m²]"] = sum(Strombedarf["WP"]) / Control.gfa
		DS.scraper.generell["stromverbrauch E-Mobilität [kWh/Auto]"] = DS.ZV.verbrauchFahrenEmobilität / Control.anzAutos

		#PV
		DS.scraper.generell["pvProduktion [kWh]"] = sum(PV)
		DS.scraper.generell["pvProduktionGfa [kWh/m²]"] = sum(PV) / Control.gfa

		#Indikatoren
		DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] = DS.ZV.fehlgeschlageneFahrversuche / DS.ZV.fahrversuche * 100
		DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilität [%/Auto]"] = np.mean(DS.zeitVar.ungenutzteLadung) / Control.anzAutos
		DS.scraper.indikatoren["erhöhung Eigenverbrauch E-Mobilität [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["erhöhung Eigenverbrauch Zureisende [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto [Anzahl]"] = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto ohne LC [Anzahl]"] = PVDaten[4]
		DS.scraper.indikatoren["Reserveautos [Anzahl]"] = sum(DS.zeitVar.anzahlReserveAutos) / len(DS.zeitVar.anzahlReserveAutos)
		

		#Verbrauch der E-Mobilität zum Fahren
		DS.scraper.eMobilitätFahren["Gesamt [kWh/Auto]"] = DS.ZV.verbrauchFahrenEmobilität / Control.anzAutos
		DS.scraper.eMobilitätFahren["Lokal [kWh/Auto]"] = sum(DS.zeitVar.fahrverbrauchLokal) / Control.anzAutos
		DS.scraper.eMobilitätFahren["Netz [kWh/Auto]"] = sum(DS.zeitVar.fahrverbrauchNetz) / Control.anzAutos
		DS.scraper.eMobilitätFahren["externe Ladung [kWh/Auto]"] = sum(DS.zeitVar.LadeLeistungExterneStationen) / Control.anzAutos

		#Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
		daten = CalcEMobilityBuildingEnergyFlows(discharge= sum(DS.zeitVar.eMobilityDischarge), charge= sum(DS.zeitVar.eMobilityCharge),
										  car= Control.li_Autos[0],externCharge= sum(DS.zeitVar.LadeLeistungExterneStationen))
		DS.scraper.eMobilitätGebäude["EMobilitätzuGebäude [kWh/Auto]"] = daten[0] * Control.li_Autos[0].effizienz / Control.anzAutos
		DS.scraper.eMobilitätGebäude["Fahrverbrauch [kWh/Auto]"] = daten[1] / Control.anzAutos
		DS.scraper.eMobilitätGebäude["Lade/Entladeverluste [kWh/Auto]"] = daten[2] / Control.anzAutos
		DS.scraper.eMobilitätGebäude["GebäudezuEMobilität [kWh/Auto]"] = sum(DS.zeitVar.eMobilityCharge) * Control.li_Autos[0].effizienz / Control.anzAutos
		DS.scraper.eMobilitätGebäude["EMobilitätzuGebäude [kWh/m²]"] = daten[0] * Control.li_Autos[0].effizienz / Control.gfa
		DS.scraper.eMobilitätGebäude["Lade/Entladeverluste [kWh/m²]"] = daten[2] / Control.gfa
		DS.scraper.eMobilitätGebäude["GebäudezuEMobilität [kWh/m²]"] = sum(DS.zeitVar.eMobilityCharge) * Control.li_Autos[0].effizienz / Control.gfa
	
		#PV-Daten vor E-Mobilität
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)
		DS.scraper.pvVorEMobilität["Eigenverbrauch [kWh/m²]"] = daten[0] / Control.gfa
		DS.scraper.pvVorEMobilität["Einspeisung [kWh/m²]"] = daten[1] / Control.gfa
		DS.scraper.pvVorEMobilität["Netzbezug [kWh/m²]"] = abs(sum([x for x in DS.zeitVar.resLastBeforeEMobility if x > 0])) / Control.gfa
		
		#PV-Daten nach E-Mobilität
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)
		DS.scraper.pvNachEMobilität["Eigenverbrauch [kWh/m²]"] = daten[0] / Control.gfa
		DS.scraper.pvNachEMobilität["Einspeisung [kWh/m²]"] = daten[1] / Control.gfa
		DS.scraper.pvNachEMobilität["Netzbezug [kWh/m²]"] = abs(sum([x for x in DS.zeitVar.resLastAfterEMobility if x > 0])) / Control.gfa

		#PV-Daten nach Zureisenden
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)
		DS.scraper.pvNachZureisenden["Eigenverbrauch [kWh/m²]"] = daten[0] / Control.gfa
		DS.scraper.pvNachZureisenden["Einspeisung [kWh/m²]"] = daten[1] / Control.gfa
		DS.scraper.pvNachZureisenden["Netzbezug [kWh/m²]"] = abs(sum([x for x in DS.zeitVar.resLastAfterZureisende if x > 0])) / Control.gfa
		DS.scraper.zureisenden["Ladung [kWh/m²]"] = sum(DS.zeitVar.LadeLeistungAußenstehende) / Control.gfa	

		#Primärenergie
		PE_Fossil = Control.anzPers*(1-Control.percent)*80/100*personenKilometerElektrisch*1.2 / Control.gfa
		if scenariosWärme[i] == "FW":
			PE_FW = abs(sum(pd.read_csv("./Ergebnis/Strombedarf_FW.csv", decimal=",", sep=";", encoding= "cp1252")["Wärmebedarf_FW"].tolist()) / Control.gfa * PE_CO2.fernwärmePrimärenergie)
		else:
			PE_FW = 0
		DS.scraper.primärenergie["PE_OhnePV [kWh/m²]"] = sum(dict_PE_CO2["PE_OhnePV [kWh/m²]"]) + PE_Fossil + PE_FW
		DS.scraper.primärenergie["PE_MitPV [kWh/m²]"] = sum(dict_PE_CO2["PE_MitPV [kWh/m²]"]) + PE_Fossil + PE_FW
		DS.scraper.primärenergie["PE_MitEmobilität [kWh/m²]"] = sum(dict_PE_CO2["PE_MitLC [kWh/m²]"]) + PE_Fossil + PE_FW

		#CO2-Emissionen
		CO2_Fossil = PE_Fossil * 0.250
		CO2_FW = PE_FW * PE_CO2.fernwärmeEmissionen
		DS.scraper.CO2Emissionen["CO2_OhnePV [kg/m²]"] = sum(dict_PE_CO2["CO2_OhnePV [kg/m²]"]) + CO2_Fossil + CO2_FW
		DS.scraper.CO2Emissionen["CO2_MitPV [kg/m²]"] = sum(dict_PE_CO2["CO2_MitPV [kg/m²]"]) + CO2_Fossil + CO2_FW
		DS.scraper.CO2Emissionen["CO2_MitEmobilität [kg/m²]"] = sum(dict_PE_CO2["CO2_MitLC [kg/m²]"]) + CO2_Fossil + CO2_FW

		#Export Data
		DS.scraper.Export(f"{scen}_{scenariosWärme[i]}")	

		DS.zeitVar.Export(f"{scen}_{scenariosWärme[i]}")


		if scenariosWärme[i] == "WP" and scen == "PV":
			pass
			#PlotStatusCollection(DS.zeitVar.StateofCars)
			#PlotPersonStatus(DS.zeitVar.StateofDrivingPersons)
			#PlotEinflussLDC(gesamtBedarf, PV, DS.zeitVar.entladungLokal, DS.zeitVar.pvChargingHourly) #DS.zeitVar.pvChargingHourly
			#PlotVerteilungen(DS.zeitVar.eMobilityCharge, "Ladeleistung")
			#PlotVerteilungen(DS.zeitVar.eMobilityDischarge, "EntladeLeistung")
			#PlotVerteilungen(DS.zeitVar.LadeLeistungAußenstehende, "LadeLeistung Zureisende")
			#PlotVerteilungen(gesamtBedarf, "Gebäudebedarf")


		
		##PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)

	


