# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus, PlotVerteilungen, PlotEinflussLDC

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows

from ReadInput import inputData

from PE_CO2 import PE_CO2

import Plotting.DataScraper as DS

import numpy as np

AutoDaten = inputData["AutoDaten"]
PersonenDaten = inputData["PersonenDaten"]
ExterneDaten = inputData["ExterneDaten"]
LadeDaten = inputData["LadeDaten"]["distMinLadung"]

scenarios = ["PV", "PV_max"]
dataW�rme = [[0]*8760,Strombedarf["WP"]]
scenariosW�rme = ["FW","WP"]

for scen in scenarios:
	for i, scenW�rme in enumerate(dataW�rme):
		DS.scraper.__init__()
		DS.ZV.__init__()
		DS.zeitVar.__init__()
		Control = LadeController(AutoDaten= AutoDaten, distMinLadung= LadeDaten, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
		PV = DefinePV(scen)

		gesamtBedarf = [a + b + c + d for a,b,c,d in zip(Strombedarf["Wohnen"], Strombedarf["Gewerbe"],Strombedarf["Schule"],scenW�rme)]

		for hour in range(8760):
			pv = PV[hour]
			bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + scenW�rme[hour]

			#resLast = 1 - pv
			resLast = bedarf - pv
			DS.zeitVar.resLastBeforeEMobility[hour] = resLast
			Control.CheckTimestep(hour= hour,resLast= resLast)
			if DS.zeitVar.gridChargingHourly[hour]+DS.zeitVar.pvChargingHourly[hour] > 0:
				DS.zeitVar.fahrverbrauchLokal[hour] = DS.zeitVar.pvChargingHourly[hour]/(DS.zeitVar.gridChargingHourly[hour]+DS.zeitVar.pvChargingHourly[hour])*DS.zeitVar.carDemandHourly[hour]
				DS.zeitVar.fahrverbrauchNetz[hour] = DS.zeitVar.gridChargingHourly[hour]/(DS.zeitVar.gridChargingHourly[hour]+DS.zeitVar.pvChargingHourly[hour])*DS.zeitVar.carDemandHourly[hour]
		
		PE_CO2.CalcPE(szen= scenariosW�rme[i], name= "OhnePV", gfa= Control.gfa, resLast= gesamtBedarf)
		PE_CO2.CalcPE(szen= scenariosW�rme[i], name= "MitPV", gfa= Control.gfa, resLast= DS.zeitVar.resLastBeforeEMobility)
		PE_CO2.CalcPE(szen= scenariosW�rme[i], name= "MitLC", gfa= Control.gfa, resLast= DS.zeitVar.resLastAfterEMobility)
		PE_CO2.CalcPE(szen= scenariosW�rme[i], name= "MitZureisende", gfa= Control.gfa, resLast= DS.zeitVar.resLastAfterZureisende)
				
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
		DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilit�t [%]"] = np.mean(DS.zeitVar.ungenutzteLadung)
		DS.scraper.indikatoren["erh�hung Eigenverbrauch E-Mobilit�t [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["erh�hung Eigenverbrauch Zureisende [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto [Anzahl]"] = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos

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

		#Export Data
		DS.scraper.Export(f"{scen}_{scenariosW�rme[i]}")	

		DS.zeitVar.Export(f"{scen}_{scenariosW�rme[i]}")
		#PlotStatusCollection(DS.zeitVar.StateofCars)
		#PlotPersonStatus(DS.zeitVar.StateofDrivingPersons)
		#PlotEinflussLDC(gesamtBedarf, PV, DS.zeitVar.EntladeLeistung)
		#PlotVerteilungen(DS.zeitVar.LadeLeistung, "Ladeleistung")
		#PlotVerteilungen(DS.zeitVar.EntladeLeistung, "EntladeLeistung")
		#PlotVerteilungen(DS.zeitVar.LadeLeistungAu�enstehende, "LadeLeistung Zureisende")
		#PlotVerteilungen(gesamtBedarf, "Geb�udebedarf")


		
		##PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)

	


