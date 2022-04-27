
import pandas as pd
import numpy as np
import math
import csv

from Building import Building
from Wärmepumpe_Speicher import Speicher, Wärmepumpe
from Helper import *
u_Wand = 0.15
u_Boden = 0.2
u_Dach = 0.1
u_Fenster = 0.8

W1 = Building( wand = {"Fläche":2217.63,"U-Wert":u_Wand},
			  fenster = {"Fläche":1478.42,"U-Wert":u_Fenster},
			  dach = {"Fläche":1973.94,"U-Wert":u_Dach},
			  boden = {"Fläche":1973.94,"U-Wert":u_Boden})

W2 = Building( wand = {"Fläche":3022.56,"U-Wert":u_Wand},
			  fenster = {"Fläche":2015.04,"U-Wert":u_Fenster},
			  dach = {"Fläche":2509.2,"U-Wert":u_Dach},
			  boden = {"Fläche":2509.2,"U-Wert":u_Boden})

W3 = Building( wand = {"Fläche":3370.92,"U-Wert":u_Wand},
			  fenster = {"Fläche":2247.28,"U-Wert":u_Fenster},
			  dach = {"Fläche":1710.52,"U-Wert":u_Dach},
			  boden = {"Fläche":1710.52,"U-Wert":u_Boden})

W4 = Building( wand = {"Fläche":3620.23,"U-Wert":u_Wand},
			  fenster = {"Fläche":2413.48,"U-Wert":u_Fenster},
			  dach = {"Fläche":1114.8,"U-Wert":u_Dach},
			  boden = {"Fläche":1114.8,"U-Wert":u_Boden})

class Simulation():

	def __init__(self):		
		#Jedes Teilgebäude wird in einem Dictionary gesammelt
		self.dic_buildings = {"W1":W1,"W2":W2,"W3":W3,"W4":W4}  
		
		self.ta = np.genfromtxt("./Data/climate.csv", delimiter=";", usecols = (1), skip_header = 1)

		self.electricProfile = pd.read_csv("./Data/Stromprofil.csv", delimiter=";", decimal = ",")

		print(self.electricProfile.info())
		self.time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[d]')

		speicher = Speicher(100000, 0.2)
		self.WP  = Wärmepumpe(speicher, COP_HZG= 5, COP_WW= 3, Pel= 100)


	def Simulate(self):

		for hour in range(0,8760):

			stromVerbrauch = GetStromProfil(hour)  #Ruft den aktuellen Stromverbrauch ab in W 

			qHLSum = 0

			for key,building in self.dic_buildings.items():
				qHLSum += building.CalcThermalFlows(self.ta[hour], DetermineHourofDay(hour))

			self.WP.speicher.SpeicherEntladen(qHLSum, self.WP.hystEin


		
test = Simulation()


test.Simulate()






