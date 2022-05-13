﻿
import pandas as pd
import numpy as np
import math
import csv

from Building import Building
from Wärmepumpe_Speicher import Speicher, Wärmepumpe
from Helper import *
u_Wand = 0.2
u_Boden = 0.25
u_Dach = 0.15
u_Fenster = 0.9

W1 = Building( wand = {"Fläche":2217.63,"U-Wert":u_Wand},
			  fenster = {"Fläche":1478.42,"U-Wert":u_Fenster},
			  dach = {"Fläche":1973.94,"U-Wert":u_Dach},
			  boden = {"Fläche":1973.94,"U-Wert":u_Boden}, 
			  gfa = 11844, volumen=41454,
			  anzPersonen=311, stromVerbrauch = 840500)

W2 = Building( wand = {"Fläche":3022.56,"U-Wert":u_Wand},
			  fenster = {"Fläche":2015.04,"U-Wert":u_Fenster},
			  dach = {"Fläche":2509.2,"U-Wert":u_Dach},
			  boden = {"Fläche":2509.2,"U-Wert":u_Boden},
			  gfa = 15361, volumen=57282,
			  anzPersonen=405, stromVerbrauch = 1095100)

W3 = Building( wand = {"Fläche":3370.92,"U-Wert":u_Wand},
			  fenster = {"Fläche":2247.28,"U-Wert":u_Fenster},
			  dach = {"Fläche":1710.52,"U-Wert":u_Dach},
			  boden = {"Fläche":1710.52,"U-Wert":u_Boden},
			  gfa = 13700, volumen=49750,
			  anzPersonen=331, stromVerbrauch = 895700)

W4 = Building( wand = {"Fläche":3620.23,"U-Wert":u_Wand},
			  fenster = {"Fläche":2413.48,"U-Wert":u_Fenster},
			  dach = {"Fläche":1114.8,"U-Wert":u_Dach},
			  boden = {"Fläche":1114.8,"U-Wert":u_Boden},
			  gfa = 10976, volumen=36270,
			  anzPersonen=288, stromVerbrauch = 779000)


class Simulation():

	def __init__(self):		
		#Jedes Teilgebäude wird in einem Dictionary gesammelt
		self.dic_buildings = {"W1":W1,"W2":W2,"W3":W3,"W4":W4}  
		for key,item in self.dic_buildings.items():
			item.InitHeizlast()


		self.ta = np.genfromtxt("./Data/climate.csv", delimiter=";", usecols = (1), skip_header = 1)


	def InitSzenarioWP(self, dic_buildings):
		COP_HZG = 5
		COP_WW = 3

		speicherW1 = Speicher(10000)
		dic_buildings["W1"].WP = Wärmepumpe(speicherW1, COP_HZG= COP_HZG, COP_WW= COP_WW, Pel= 250)

		speicherW2 = Speicher(10000)
		dic_buildings["W2"].WP = Wärmepumpe(speicherW2, COP_HZG= COP_HZG, COP_WW= COP_WW, Pel= 250)

		speicherW3 = Speicher(10000)
		dic_buildings["W3"].WP = Wärmepumpe(speicherW3, COP_HZG= COP_HZG, COP_WW= COP_WW, Pel= 250)

		speicherW4 = Speicher(10000)
		dic_buildings["W4"].WP = Wärmepumpe(speicherW4, COP_HZG= COP_HZG, COP_WW= COP_WW, Pel= 250)


	def InitSzenarioFW(self):
		pass

	def Simulate(self):
		self.InitSzenarioWP(self.dic_buildings)
		for hour in range(0,100):

			

			qHLSum = 0

			for key,building in self.dic_buildings.items():

				stromVerbrauch = GetStromProfil(hour) / 10**6 * building.stromVerbrauch

				qHLSum = building.CalcThermalFlows(ta=self.ta[hour], hour=hour,
									  anz_Personen=building.anzPersonen, strom = stromVerbrauch) / 1000
				building.WP.speicher.SpeicherEntladen(qHLSum, building.WP.hystEin)
				building.WP.CheckSpeicher(mode = "HZG")
				print(f"Gebäude: {key}")
				print(f"Heizlast: {round(qHLSum/1000,2)} MWh")
				print(f"Status WP: {building.WP.bIsOn}")
				print(f"Ladestand Speicher: {round(building.WP.speicher.Speicherstand(),3)}")
				print("------------------")
			print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")





		
test = Simulation()


test.Simulate()





