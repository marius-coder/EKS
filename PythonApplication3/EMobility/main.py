# -*- coding: <latin-1> -*-

from PlotMobility import PlotStatusCollection, PlotSample, PlotUseableCapacity, PlotSOC, PlotPersonStatus, PlotResiduallast, PlotEigenverbrauch, PlotEigenverbrauchmitAutoeinspeisung, PlotPieDischarge

from Strom.PV import Strombedarf, PV

from LadeController_Main import LadeController

import Plotting.DataScraper as DS


#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#60% mussen 75% geladen sein
	"30" : 0.5		#30% mussen 50% geladen sein
	}



Control = LadeController(anzAutos= 120, distMinLadung= distMinLadung, maxLadung = 41)

for hour in range(8760):

	pv = PV[hour]
	bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour]
	
	#resLast = 1 - pv
	resLast = bedarf - pv
	DS.Scraper.resLast.append(resLast)
	#print(f"Stunde: {hour}")
	#print(f"Residuallast: {resLast} kWh")
	Control.CheckTimestep(hour= hour,resLast= resLast)



PlotPieDischarge(sum(DS.Scraper.resLastDifferenceAfterDischarge), sum(DS.Scraper.resLastDifference), Control.li_Autos[0])
PlotEigenverbrauchmitAutoeinspeisung(PV,DS.Scraper.resLast, DS.Scraper.resLastDifference)

PlotEigenverbrauch(PV,DS.Scraper.resLast)
PlotResiduallast(PV,Strombedarf["Wohnen"].tolist(),DS.Scraper.resLast)
PlotPersonStatus(DS.Scraper.li_state)
PlotStatusCollection(DS.Scraper.li_stateCars)
#PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)


