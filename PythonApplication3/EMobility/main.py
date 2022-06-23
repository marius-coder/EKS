# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus, PlotVerteilungen, PlotEinflussLDC

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows

from ReadInput import inputData

import Plotting.DataScraper as DS

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
			DS.zeitVar.fahrverbrauchLokal[hour] = DS.zeitVar.pvChargingHourly[hour]/(DS.zeitVar.gridChargingHourly[hour]+DS.zeitVar.pvChargingHourly[hour])*DS.zeitVar.carDemandHourly[hour]
			DS.zeitVar.fahrverbrauchNetz[hour] = DS.zeitVar.gridChargingHourly[hour]/(DS.zeitVar.gridChargingHourly[hour]+DS.zeitVar.pvChargingHourly[hour])*DS.zeitVar.carDemandHourly[hour]

		personenKilometerElektrisch = 0
		for person in Control.persons:
			personenKilometerElektrisch += person.wegMitAuto 
		print(personenKilometerElektrisch / len(Control.persons))
		#Personenkilometer
		DS.scraper.generell["personenKilometer Elektrisch durch. [km]"] = personenKilometerElektrisch / len(Control.persons)
		DS.scraper.generell["personenKilometer Elektrisch [km]"] = personenKilometerElektrisch
		DS.scraper.generell["personenKilometer Fossil [km]"] = Control.anzPersonen * Control.personenKilometer - personenKilometerElektrisch

		#Stromverbrauch
		DS.scraper.generell["stromverbrauch Wohnen [kWh]"] = sum(Strombedarf["Wohnen"])
		DS.scraper.generell["stromverbrauch Gewerbe [kWh]"] = sum(Strombedarf["Gewerbe"])
		DS.scraper.generell["stromverbrauch Schule [kWh]"] = sum(Strombedarf["Schule"])
		DS.scraper.generell["stromverbrauch WP [kWh]"] = sum(Strombedarf["WP"])
		DS.scraper.generell["stromverbrauch E-Mobilit�t [kWh]"] = DS.ZV.verbrauchFahrenEmobilit�t

		#PV
		DS.scraper.generell["pvProduktion [kWh]"] = sum(PV)
		DS.scraper.generell["pvProduktionGfa [kWh]"] = sum(PV) / Control.gfa

		#Indikatoren
		DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] = DS.ZV.fehlgeschlageneFahrversuche / DS.ZV.fahrversuche * 100
		DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilit�t [%]"] = 100 - DS.ZV.aktuelleLadung / DS.ZV.maxLadung * 100
		DS.scraper.indikatoren["erh�hung Eigenverbrauch [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] \
																/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)[0] * 100 - 100
		DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto [Anzahl]"] = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos
		DS.scraper.indikatoren["Ladevorg�nge pro Auto [Anzahl]"] = DS.ZV.counterCharging / Control.anzAutos
		DS.scraper.indikatoren["Entladevorg�nge pro Auto [Anzahl]"] = DS.ZV.counterDischarging / Control.anzAutos

		#Verbrauch der E-Mobilit�t zum Fahren
		DS.scraper.eMobilit�tFahren["Gesamt [kWh]"] = DS.ZV.verbrauchFahrenEmobilit�t
		DS.scraper.eMobilit�tFahren["Lokal [kWh]"] = sum(DS.zeitVar.fahrverbrauchLokal)
		DS.scraper.eMobilit�tFahren["Netz [kWh]"] = sum(DS.zeitVar.fahrverbrauchNetz)
		DS.scraper.eMobilit�tFahren["externe Ladung [kWh]"] = sum(DS.zeitVar.LadeLeistungExterneStationen)

		#Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
		daten = CalcEMobilityBuildingEnergyFlows(discharge= sum(DS.zeitVar.eMobilityDischarge), charge= sum(DS.zeitVar.eMobilityCharge),
										  car= Control.li_Autos[0],externCharge= sum(DS.zeitVar.LadeLeistungExterneStationen))
		DS.scraper.eMobilit�tGeb�ude["EMobilit�tzuGeb�ude [kWh]"] = daten[0]
		DS.scraper.eMobilit�tGeb�ude["Fahrverbrauch [kWh]"] = daten[1]
		DS.scraper.eMobilit�tGeb�ude["Lade/Entladeverluste [kWh]"] = daten[2]
		DS.scraper.eMobilit�tGeb�ude["Geb�udezuEMobilit�t [kWh]"] = sum(DS.zeitVar.eMobilityCharge)
	
		#PV-Daten vor E-Mobilit�t
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)
		DS.scraper.pvVorEMobilit�t["Eigenverbrauch [kWh]"] = daten[0]
		DS.scraper.pvVorEMobilit�t["Einspeisung [kWh]"] = daten[1]
		DS.scraper.pvVorEMobilit�t["Netzbezug [kWh]"] = abs(sum([x for x in DS.zeitVar.resLastBeforeEMobility if x > 0])) 
		
		#PV-Daten nach E-Mobilit�t
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)
		DS.scraper.pvNachEMobilit�t["Eigenverbrauch [kWh]"] = daten[0]
		DS.scraper.pvNachEMobilit�t["Einspeisung [kWh]"] = daten[1]
		DS.scraper.pvNachEMobilit�t["Netzbezug [kWh]"] = abs(sum([x for x in DS.zeitVar.resLastAfterEMobility if x > 0]))  

		#PV-Daten nach Zureisenden
		daten = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)
		DS.scraper.pvNachZureisenden["Eigenverbrauch [kWh]"] = daten[0]
		DS.scraper.pvNachZureisenden["Einspeisung [kWh]"] = daten[1]
		DS.scraper.pvNachZureisenden["Netzbezug [kWh]"] = abs(sum([x for x in DS.zeitVar.resLastAfterZureisende if x > 0]))  
		DS.scraper.zureisenden["Ladung [kWH]"] = sum(DS.zeitVar.LadeLeistungAu�enstehende)		

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

	


