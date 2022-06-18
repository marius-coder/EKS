# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows

import Plotting.DataScraper as DS



#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% m�ssen voll geladen sein
	"60" : 0.75,	#60% m�ssen 75% geladen sein
	"30" : 0.5		#30% m�ssen 50% geladen sein
	}

scenarios = ["PV", "PV_max"]


for Scen in scenarios:
	DS.scraper.__init__()
	DS.ZV.__init__()
	DS.zeitVar.__init__()
	Control = LadeController(anzAutos= 90, distMinLadung= distMinLadung, maxLadung = 41, personenKilometer= 5527, gfa= 76417.24, percentAbweichung= 0.25)
	PV = DefinePV(Scen)

	for hour in range(8760):

		pv = PV[hour]
		bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + Strombedarf["WP"][hour]
	
		#resLast = 1 - pv
		resLast = bedarf - pv
		DS.ZV.resLastBeforeEMobility[hour] = resLast
		Control.CheckTimestep(hour= hour,resLast= resLast)


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
	DS.scraper.indikatoren["erh�hung Eigenverbrauch [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastAfterEMobility)[0] \
															/ CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastBeforeEMobility)[0] * 100 - 100
	DS.scraper.indikatoren["LadeEntlade_Zyklen ohne EMobilit�t pro Auto [Anzahl]"] = DS.ZV.gridCharging / DS.ZV.maxLadung / Control.anzAutos
	DS.scraper.indikatoren["LadeEntlade_Zyklen mit EMobilit�t pro Auto [Anzahl]"] = (sum(DS.ZV.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos
	DS.scraper.indikatoren["Ladevorg�nge [Anzahl]"] = DS.ZV.counterCharging / Control.anzAutos
	DS.scraper.indikatoren["Entladevorg�nge [Anzahl]"] = DS.ZV.counterDischarging / Control.anzAutos

	#Verbrauch der E-Mobilit�t zum Fahren
	DS.scraper.eMobilit�tFahren["Gesamt [kWh]"] = DS.ZV.verbrauchFahrenEmobilit�t
	DS.scraper.eMobilit�tFahren["Lokal [kWh]"] = DS.ZV.verbrauchFahrenEmobilit�t - DS.ZV.gridCharging * Control.li_Autos[0].effizienz
	DS.scraper.eMobilit�tFahren["Netz [kWh]"] = DS.ZV.gridCharging * Control.li_Autos[0].effizienz

	#Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
	daten = CalcEMobilityBuildingEnergyFlows(sum(DS.ZV.eMobilityDischarge), sum(DS.ZV.eMobilityCharge), Control.li_Autos[0])
	DS.scraper.eMobilit�tGeb�ude["EMobilit�tzuGeb�ude [kWh]"] = daten[0]
	DS.scraper.eMobilit�tGeb�ude["Fahrverbrauch [kWh]"] = daten[1]
	DS.scraper.eMobilit�tGeb�ude["Lade/Entladeverluste [kWh]"] = daten[2]
	DS.scraper.eMobilit�tGeb�ude["Geb�udezuEMobilit�t [kWh]"] = sum(DS.ZV.eMobilityCharge)
	
	#PV-Daten vor E-Mobilit�t
	daten = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastBeforeEMobility)
	DS.scraper.pvVorEMobilit�t["Eigenverbrauch [kWh]"] = daten[0]
	DS.scraper.pvVorEMobilit�t["Einspeisung [kWh]"] = daten[1]
	DS.scraper.pvVorEMobilit�t["Netzbezug [kWh]"] = abs(sum([x for x in DS.ZV.resLastBeforeEMobility if x > 0])) 
		
	#PV-Daten nach E-Mobilit�t
	daten = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastAfterEMobility)
	DS.scraper.pvNachEMobilit�t["Eigenverbrauch [kWh]"] = daten[0]
	DS.scraper.pvNachEMobilit�t["Einspeisung [kWh]"] = daten[1]
	DS.scraper.pvNachEMobilit�t["Netzbezug [kWh]"] = abs(sum([x for x in DS.ZV.resLastAfterDischarging if x > 0]))  

	#Export Data
	DS.scraper.Export(Scen)

	#Zeitvariablen
	DS.zeitVar.LadeLeistung = DS.ZV.eMobilityCharge
	DS.zeitVar.EntladeLeistung = DS.ZV.eMobilityDischarge
	

	#PlotPieDischarge(sum(DS.Scraper.resLastDifferenceAfterDischarge), sum(DS.Scraper.resLastDifference), Control.li_Autos[0])
	#PlotEigenverbrauchmitAutoeinspeisung(PV,DS.Scraper.resLast, DS.Scraper.resLastDifference)

	#PlotEigenverbrauch(PV,DS.Scraper.resLast)
	#PlotResiduallast(PV,Strombedarf["Wohnen"].tolist(),DS.Scraper.resLast)	
	PlotLadegang(DS.zeitVar.LadeLeistung)
	PlotStatusCollection(DS.zeitVar.StateofCars)
	PlotPersonStatus(DS.zeitVar.StateofDrivingPersons)
	##PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)

	


