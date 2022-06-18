# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows

import Plotting.DataScraper as DS



#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% müssen voll geladen sein
	"60" : 0.75,	#60% müssen 75% geladen sein
	"30" : 0.5		#30% müssen 50% geladen sein
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
	DS.scraper.generell["stromverbrauch E-Mobilität [kWh]"] = DS.ZV.verbrauchFahrenEmobilität

	#PV
	DS.scraper.generell["pvProduktion [kWh]"] = sum(PV)
	DS.scraper.generell["pvProduktionGfa [kWh]"] = sum(PV) / Control.gfa

	#Indikatoren
	DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] = DS.ZV.fehlgeschlageneFahrversuche / DS.ZV.fahrversuche * 100
	DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilität [%]"] = 100 - DS.ZV.aktuelleLadung / DS.ZV.maxLadung * 100
	DS.scraper.indikatoren["erhöhung Eigenverbrauch [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastAfterEMobility)[0] \
															/ CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastBeforeEMobility)[0] * 100 - 100
	DS.scraper.indikatoren["LadeEntlade_Zyklen ohne EMobilität pro Auto [Anzahl]"] = DS.ZV.gridCharging / DS.ZV.maxLadung / Control.anzAutos
	DS.scraper.indikatoren["LadeEntlade_Zyklen mit EMobilität pro Auto [Anzahl]"] = (sum(DS.ZV.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos
	DS.scraper.indikatoren["Ladevorgänge [Anzahl]"] = DS.ZV.counterCharging / Control.anzAutos
	DS.scraper.indikatoren["Entladevorgänge [Anzahl]"] = DS.ZV.counterDischarging / Control.anzAutos

	#Verbrauch der E-Mobilität zum Fahren
	DS.scraper.eMobilitätFahren["Gesamt [kWh]"] = DS.ZV.verbrauchFahrenEmobilität
	DS.scraper.eMobilitätFahren["Lokal [kWh]"] = DS.ZV.verbrauchFahrenEmobilität - DS.ZV.gridCharging * Control.li_Autos[0].effizienz
	DS.scraper.eMobilitätFahren["Netz [kWh]"] = DS.ZV.gridCharging * Control.li_Autos[0].effizienz

	#Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
	daten = CalcEMobilityBuildingEnergyFlows(sum(DS.ZV.eMobilityDischarge), sum(DS.ZV.eMobilityCharge), Control.li_Autos[0])
	DS.scraper.eMobilitätGebäude["EMobilitätzuGebäude [kWh]"] = daten[0]
	DS.scraper.eMobilitätGebäude["Fahrverbrauch [kWh]"] = daten[1]
	DS.scraper.eMobilitätGebäude["Lade/Entladeverluste [kWh]"] = daten[2]
	DS.scraper.eMobilitätGebäude["GebäudezuEMobilität [kWh]"] = sum(DS.ZV.eMobilityCharge)
	
	#PV-Daten vor E-Mobilität
	daten = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastBeforeEMobility)
	DS.scraper.pvVorEMobilität["Eigenverbrauch [kWh]"] = daten[0]
	DS.scraper.pvVorEMobilität["Einspeisung [kWh]"] = daten[1]
	DS.scraper.pvVorEMobilität["Netzbezug [kWh]"] = abs(sum([x for x in DS.ZV.resLastBeforeEMobility if x > 0])) 
		
	#PV-Daten nach E-Mobilität
	daten = CalcEigenverbrauch(pv= PV, resLast= DS.ZV.resLastAfterEMobility)
	DS.scraper.pvNachEMobilität["Eigenverbrauch [kWh]"] = daten[0]
	DS.scraper.pvNachEMobilität["Einspeisung [kWh]"] = daten[1]
	DS.scraper.pvNachEMobilität["Netzbezug [kWh]"] = abs(sum([x for x in DS.ZV.resLastAfterDischarging if x > 0]))  

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

	


