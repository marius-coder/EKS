# -*- coding: cp1252 -*-

from PlotMobility import PlotLadegang, PlotStatusCollection, PlotPersonStatus, PlotVerteilungen, PlotEinflussLDC
from Strom.PV import Strombedarf, DefinePV
from LadeController_Main import LadeController
from Ladecontroller_Helper import CalcEigenverbrauch, CalcEMobilityBuildingEnergyFlows
import Plotting.DataScraper as DS
import numpy as np

inputData = {
	"AutoDaten" : {
		"Anzahl Autos" : 100,
		"maxLadung" : 41,
		"Verbrauch" : 0.17,
		"Lade/Entladeleistung" : 15,
		"Effizienz" : 95,
		},	
	"PersonenDaten" : {
		"personenKilometer" : 5527,
		"anzPersonen" : 1335,
		"percentMobilität" : 30,
		"gfa" : 76417.24,
		"percentAbweichung" : 25,
		"Safety" : 1.2,
		"Verbreitung externe Ladestationen" : 0
		},
	"ExterneDaten" : {
		"Info Lehrpersonal" : {
			"Ladung" : 41,
			"Anzahl" : 30,
			"Prozent Mitmachende" : 30,
			},
		"Info Sonstiges Personal" : {
			"Ladung" : 41,
			"Anzahl" : 200,
			"Prozent Mitmachende" : 0,
			}
		},
	"LadeDaten" : {	
		"distMinLadung" : {}
		}
	}

AutoDaten = inputData["AutoDaten"]
PersonenDaten = inputData["PersonenDaten"]
ExterneDaten = inputData["ExterneDaten"]


DS.scraper.__init__()
DS.ZV.__init__()
DS.zeitVar.__init__()

PV = DefinePV("PV_max")

gesamtBedarf = [a + b + c + d for a,b,c,d in zip(Strombedarf["Wohnen"], Strombedarf["Gewerbe"],Strombedarf["Schule"],Strombedarf["WP"])]


import random as r

def random_sum_to(n, num_terms = None):
    num_terms = (num_terms or r.randint(2, n)) - 1
    a = r.sample(range(1, n), num_terms) + [0, n]
    list.sort(a)
    return [a[i+1] - a[i] for i in range(len(a) - 1)]

test = 0
for _ in range(1000):
	anteil = random_sum_to(100, 5)
	ladung = []
	for _ in range(5):
		ladung.append(int(round(r.uniform(1,100),0)))
	#if sum(ladung) < 300:
	#	continue
	#key= Ladung, value=Anteil
	LadeDaten = {
		ladung[0] : str(anteil[0]),
		ladung[1] : str(anteil[1]),
		ladung[2] : str(anteil[2]),
		ladung[3] : str(anteil[3]),
		ladung[4] : str(anteil[4]),
		}

	Control = LadeController(AutoDaten= AutoDaten, distMinLadung= LadeDaten, PersonenDaten= PersonenDaten,
						   infoLehrpersonal= ExterneDaten["Info Lehrpersonal"], infoGewerbepersonal= ExterneDaten["Info Sonstiges Personal"])
	for hour in range(8760):
		pv = PV[hour]
		bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour] + Strombedarf["WP"] [hour]

		#resLast = 1 - pv
		resLast = bedarf - pv
		DS.zeitVar.resLastBeforeEMobility[hour] = resLast
		Control.CheckTimestep(hour= hour,resLast= resLast)


	#Indikatoren
	DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] = DS.ZV.fehlgeschlageneFahrversuche / DS.ZV.fahrversuche * 100
	DS.scraper.indikatoren["ungenutzte Ladung der E-Mobilität [%]"] = np.mean(DS.zeitVar.ungenutzteLadung)
	DS.scraper.indikatoren["erhöhung Eigenverbrauch E-Mobilität [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] \
															/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastBeforeEMobility)[0] * 100 - 100
	DS.scraper.indikatoren["erhöhung Eigenverbrauch Zureisende [%]"] = CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterZureisende)[0] \
															/ CalcEigenverbrauch(pv= PV, resLast= DS.zeitVar.resLastAfterEMobility)[0] * 100 - 100
	DS.scraper.indikatoren["LadeEntlade_Zyklen pro Auto [Anzahl]"] = (sum(DS.zeitVar.eMobilityCharge) + DS.ZV.gridCharging) / DS.ZV.maxLadung / Control.anzAutos

	if DS.scraper.indikatoren["fehlgeschlagene Fahrversuche [%]"] > 3:
		continue
	if DS.scraper.indikatoren["erhöhung Eigenverbrauch E-Mobilität [%]"] > test:
		print(f"New Record: {DS.scraper.indikatoren['erhöhung Eigenverbrauch E-Mobilität [%]']} %")
		test = DS.scraper.indikatoren["erhöhung Eigenverbrauch E-Mobilität [%]"]
		print(LadeDaten)

#Export Data
#DS.scraper.Export(f"{scen}_{scenariosWärme[i]}")	
#DS.zeitVar.Export(f"{scen}_{scenariosWärme[i]}")

print(LadeDaten)	



