# -*- coding: cp1252 -*-

from PlotMobility import PlotStatusCollection, PlotSample, PlotUseableCapacity, PlotSOC, PlotPersonStatus, PlotResiduallast, PlotEigenverbrauch, PlotEigenverbrauchmitAutoeinspeisung, PlotPieDischarge

from Strom.PV import Strombedarf, DefinePV

from LadeController_Main import LadeController

from Ladecontroller_Helper import CalcEigenverbrauch

import Plotting.DataScraper as DS



#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% müssen voll geladen sein
	"60" : 0.75,	#60% müssen 75% geladen sein
	"30" : 0.5		#30% müssen 50% geladen sein
	}

scenarios = ["PV", "PV_max"]

Control = LadeController(anzAutos= 120, distMinLadung= distMinLadung, maxLadung = 41, personenKilometer= 5527, gfa= 76417.24)
for Scen in scenarios:
	DS.scraper.__init__()
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

	#PlotPieDischarge(sum(DS.Scraper.resLastDifferenceAfterDischarge), sum(DS.Scraper.resLastDifference), Control.li_Autos[0])
	#PlotEigenverbrauchmitAutoeinspeisung(PV,DS.Scraper.resLast, DS.Scraper.resLastDifference)

	#PlotEigenverbrauch(PV,DS.Scraper.resLast)
	#PlotResiduallast(PV,Strombedarf["Wohnen"].tolist(),DS.Scraper.resLast)
	PlotPersonStatus(DS.Scraper.li_state)
	PlotStatusCollection(DS.Scraper.li_stateCars)
	##PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)

	


