# -*- coding: cp1252 -*-

from Simulation import Simulation
from PE_CO2 import konversionsfaktoren

import pandas as pd

for szen in ["FW","WP"]:
	sim = Simulation()
	sim.Simulate(szen)
	sim.GetStrombedarf(szen)
	sim.ExportData(szen)

	print(f"Summe Stromverbrauch Wohnen: {sim.summeWohnen} kWh")
	print(f"Summe Stromverbrauch Gewerbe: {sim.summeGewerbe} kWh")
	print(f"Summe Stromverbrauch Schule: {sim.summeSchule} kWh")
	print(f"Summe Stromverbrauch Gesamt: {sum(sim.summeGesamt)} kWh")

li_Strom_Wohnen_HZG = [0]*8760
li_Strom_Wohnen_WW = [0]*8760

li_Strom_Schule_HZG = [0]*8760
li_Strom_Schule_WW = [0]*8760
for key, building in sim.dic_buildings.items():

	if any(x in key for x in ["W","G"]):
		li_Strom_Wohnen_HZG = [a + b for a, b in zip(building.DF.stromWP_HZG*building.gfa, li_Strom_Wohnen_HZG)]
		li_Strom_Wohnen_WW = [a + b for a, b in zip(building.DF.stromWP_WW*building.gfa, li_Strom_Wohnen_WW)]
	else:
		li_Strom_Schule_HZG = [a + b for a, b in zip(building.DF.stromWP_HZG*building.gfa, li_Strom_Schule_HZG)]
		li_Strom_Schule_WW = [a + b for a, b in zip(building.DF.stromWP_WW*building.gfa, li_Strom_Schule_WW)]


df = pd.DataFrame()

df["Strom_Wohnen_HZG [kWh]"] = li_Strom_Wohnen_HZG
df["Strom_Wohnen_WW [kWh]"] = li_Strom_Wohnen_WW
df["Strom_Schule_HZG [kWh]"] = li_Strom_Schule_HZG
df["Strom_Schule_WW [kWh]"] = li_Strom_Schule_WW
df["W1_Temp [°C]"] = sim.dic_buildings["W1"].DF.tInnen
df["W2_Temp [°C]"] = sim.dic_buildings["W2"].DF.tInnen
df["W3_Temp [°C]"] = sim.dic_buildings["W3"].DF.tInnen
df["W4_Temp [°C]"] = sim.dic_buildings["W4"].DF.tInnen
df["G1_Temp [°C]"] = sim.dic_buildings["G1"].DF.tInnen
df["G2_Temp [°C]"] = sim.dic_buildings["G2"].DF.tInnen
df["G3_Temp [°C]"] = sim.dic_buildings["G3"].DF.tInnen
df["G4_Temp [°C]"] = sim.dic_buildings["G4"].DF.tInnen
df["S1_Temp [°C]"] = sim.dic_buildings["S1"].DF.tInnen
df["S2_Temp [°C]"] = sim.dic_buildings["S2"].DF.tInnen


df.to_csv("./Ergebnis/EAS.csv", decimal= ",", sep= ";", encoding= "cp1252")
