
import pandas as pd
import numpy as np
import math
import csv

from Building import Building
from Wärmepumpe_Speicher import Speicher, Wärmepumpe
from Helper import *
from PlotHeat import PlotspezVerbrauch, PlotWochenVerbrauch, PlotInnentemperatur, PlotspezVerbrauchKWB


u_Wand = 0.2
u_Boden = 0.25
u_Dach = 0.15
u_Fenster = 0.9

W1 = Building( wand = {"Fläche":2217.63,"U-Wert":u_Wand},
			  fenster = {"Fläche":1478.42,"U-Wert":u_Fenster},
			  dach = {"Fläche":1973.94,"U-Wert":u_Dach},
			  boden = {"Fläche":1973.94,"U-Wert":u_Boden}, 
			  gfa = 9870, volumen=35532,
			  anzPersonen=311, stromVerbrauch = 346885)

W2 = Building( wand = {"Fläche":3022.56,"U-Wert":u_Wand},
			  fenster = {"Fläche":2015.04,"U-Wert":u_Fenster},
			  dach = {"Fläche":2509.2,"U-Wert":u_Dach},
			  boden = {"Fläche":2509.2,"U-Wert":u_Boden},
			  gfa = 12852, volumen=42228,
			  anzPersonen=405, stromVerbrauch = 451627)

W3 = Building( wand = {"Fläche":3370.92,"U-Wert":u_Wand},
			  fenster = {"Fläche":2247.28,"U-Wert":u_Fenster},
			  dach = {"Fläche":1710.52,"U-Wert":u_Dach},
			  boden = {"Fläche":1710.52,"U-Wert":u_Boden},
			  gfa = 10500, volumen=33750,
			  anzPersonen=331, stromVerbrauch = 368929)

W4 = Building( wand = {"Fläche":3620.23,"U-Wert":u_Wand},
			  fenster = {"Fläche":2413.48,"U-Wert":u_Fenster},
			  dach = {"Fläche":1114.8,"U-Wert":u_Dach},
			  boden = {"Fläche":1114.8,"U-Wert":u_Boden},
			  gfa = 9128, volumen=29340,
			  anzPersonen=288, stromVerbrauch = 321124)
stromKoeff = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";") #Jahresstromverbrauch bei 1 kWh Verbrauch

class Simulation():
	def __init__(self):		
		#Jedes Teilgebäude wird in einem Dictionary gesammelt
		self.dic_buildings = {"W1":W1,"W2":W2,"W3":W3,"W4":W4}  
		for key,item in self.dic_buildings.items():
			item.InitHeizlast()


		self.ta = np.genfromtxt("./Data/climate.csv", delimiter=";", usecols = (1), skip_header = 1)

		self.wwProfile = dict(pd.read_csv("./Data/Warmwasser.csv", decimal=",", sep=";"))

	def InitSzenarioWP(self, dic_buildings):
		COP_HZG = 5
		COP_WW = 3



		speicherHZG_W1 = Speicher(10000)
		dic_buildings["W1"].WP_HZG = Wärmepumpe(speicherHZG_W1, COP_HZG= COP_HZG, Pel= 250)
		speicherWW_W1 = Speicher(10000)
		dic_buildings["W1"].WP_WW = Wärmepumpe(speicherWW_W1, COP_WW= COP_WW, Pel= 250)
		dic_buildings["W1"].DF.InitSzenWP()

		speicherHZG_W2 = Speicher(10000)
		dic_buildings["W2"].WP_HZG = Wärmepumpe(speicherHZG_W2, COP_HZG= COP_HZG, Pel= 250)
		speicherWW_W2 = Speicher(10000)
		dic_buildings["W1"].WP_WW = Wärmepumpe(speicherWW_W2, COP_WW= COP_WW, Pel= 250)
		dic_buildings["W2"].DF.InitSzenWP()

		speicherHZG_W3 = Speicher(10000)
		dic_buildings["W3"].WP_HZG = Wärmepumpe(speicherHZG_W3, COP_HZG= COP_HZG, Pel= 250)
		speicherWW_W3 = Speicher(10000)
		dic_buildings["W1"].WP_WW = Wärmepumpe(speicherWW_W3, COP_WW= COP_WW, Pel= 250)
		dic_buildings["W3"].DF.InitSzenWP()

		speicherHZG_W4 = Speicher(10000)
		dic_buildings["W4"].WP_HZG = Wärmepumpe(speicherHZG_W4, COP_HZG= COP_HZG, Pel= 250)
		speicherWW_W4 = Speicher(10000)
		dic_buildings["W1"].WP_WW = Wärmepumpe(speicherWW_W4, COP_WW= COP_WW, Pel= 250)
		dic_buildings["W4"].DF.InitSzenWP()


	def InitSzenarioFW(self):
		pass

	


	def SimWP(self, building, qHLSum):

		qtoTake = building.CalcQtoTargetTemperature() * building.gfa
		if qtoTake != 0:
			building.WP_HZG.speicher.SpeicherEntladen(qtoTake, building.WP_HZG.hystEin)
			building.CalcNewTemperature(qtoTake / building.gfa)
		building.WP_HZG.CheckSpeicher(mode = "HZG")
		building.stromVerbrauchBetrieb += building.WP_HZG.PelBetrieb
		
		#print(f"Status WP: {building.WP_HZG.bIsOn}")
		#print(f"Ladestand Speicher: {round(building.WP_HZG.speicher.Speicherstand(),3)}")
		#print("------------------")

	def Simulate(self):
		self.InitSzenarioWP(self.dic_buildings)
		for hour in range(8760):			
			print(hour)
			qHLSum = 0

			for key,building in self.dic_buildings.items():

				building.stromVerbrauchBetrieb = stromKoeff["Wohnen"][hour] * building.stromVerbrauch

				qHLSum = building.CalcThermalFlows(ta=self.ta[hour], hour=hour,
									  anz_Personen=building.anzPersonen, strom = building.stromVerbrauchBetrieb) / 1000

				building.CalcNewTemperature(qHLSum * 1000)
				#print(f"Gebäude: {key}")
				#print(f"Innentemperatur: {building.ti}")

				qHLSum = qHLSum * building.gfa
				
				#print(f"Heizlast: {round(qHLSum/1000,2)} MWh")



				self.SimWP(building= building, qHLSum= qHLSum)
				building.AddDataflows(qHL= qHLSum)
			#print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")


		PlotspezVerbrauch(self.dic_buildings)
		PlotspezVerbrauchKWB(self.dic_buildings)
		PlotWochenVerbrauch(self.dic_buildings)
		PlotInnentemperatur(self.dic_buildings)

		
test = Simulation()


test.Simulate()






