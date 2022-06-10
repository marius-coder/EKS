
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

W1 = Building( wand = {"Fläche":1911.29,"U-Wert":u_Wand},
			  fenster = {"Fläche":1274.19,"U-Wert":u_Fenster},
			  dach = {"Fläche":1973.94,"U-Wert":u_Dach},
			  boden = {"Fläche":0,"U-Wert":u_Boden}, 
			  gfa = 9870, volumen=35532,
			  anzPersonen=311, stromVerbrauch = 346885)

W2 = Building( wand = {"Fläche":3556.8,"U-Wert":u_Wand},
			  fenster = {"Fläche":2371.2,"U-Wert":u_Fenster},
			  dach = {"Fläche":1224,"U-Wert":u_Dach},
			  boden = {"Fläche":0,"U-Wert":u_Boden},
			  gfa = 12852, volumen=42228,
			  anzPersonen=405, stromVerbrauch = 451627)

W3 = Building( wand = {"Fläche":2350.65,"U-Wert":u_Wand},
			  fenster = {"Fläche":1567.10,"U-Wert":u_Fenster},
			  dach = {"Fläche":748.52,"U-Wert":u_Dach},
			  boden = {"Fläche":0,"U-Wert":u_Boden},
			  gfa = 10500, volumen=33750,
			  anzPersonen=331, stromVerbrauch = 368929)

W4 = Building( wand = {"Fläche":2350.65,"U-Wert":u_Wand},
			  fenster = {"Fläche":1567.10,"U-Wert":u_Fenster},
			  dach = {"Fläche":652.8,"U-Wert":u_Dach},
			  boden = {"Fläche":0,"U-Wert":u_Boden},
			  gfa = 9128, volumen=29340,
			  anzPersonen=288, stromVerbrauch = 321124)

G1 = Building( wand = {"Fläche":262.69,"U-Wert":u_Wand},
			  fenster = {"Fläche":175.13,"U-Wert":u_Fenster},
			  dach = {"Fläche":0,"U-Wert":u_Dach},
			  boden = {"Fläche":1974,"U-Wert":u_Boden},
			  gfa = 1974, volumen=5922,
			  anzPersonen=100, stromVerbrauch = 106596)

G2 = Building( wand = {"Fläche":386.28,"U-Wert":u_Wand},
			  fenster = {"Fläche":257.52,"U-Wert":u_Fenster},
			  dach = {"Fläche":1285,"U-Wert":u_Dach},
			  boden = {"Fläche":2509,"U-Wert":u_Boden},
			  gfa = 2509, volumen=15054,
			  anzPersonen=100, stromVerbrauch = 135486)

G3 = Building( wand = {"Fläche":634.8,"U-Wert":u_Wand},
			  fenster = {"Fläche":423.2,"U-Wert":u_Fenster},
			  dach = {"Fläche":962,"U-Wert":u_Dach},
			  boden = {"Fläche":1600,"U-Wert":u_Boden},
			  gfa = 3200, volumen=16000,
			  anzPersonen=100, stromVerbrauch = 172800)

G4 = Building( wand = {"Fläche":887.59,"U-Wert":u_Wand},
			  fenster = {"Fläche":591.72,"U-Wert":u_Fenster},
			  dach = {"Fläche":462,"U-Wert":u_Dach},
			  boden = {"Fläche":462,"U-Wert":u_Boden},
			  gfa = 1848, volumen=6930,
			  anzPersonen=100, stromVerbrauch = 99792)

S1 = Building( wand = {"Fläche":2571.95,"U-Wert":u_Wand},
			  fenster = {"Fläche":1897.94,"U-Wert":u_Fenster},
			  dach = {"Fläche":2329.3,"U-Wert":u_Dach},
			  boden = {"Fläche":2948.67+2298.82,"U-Wert":u_Boden},
			  gfa = 11566.78, volumen=37579.8,
			  anzPersonen=100, stromVerbrauch = 231335)

S2 = Building( wand = {"Fläche":1231.66,"U-Wert":u_Wand},
			  fenster = {"Fläche":498.68,"U-Wert":u_Fenster},
			  dach = {"Fläche":906.67,"U-Wert":u_Dach},
			  boden = {"Fläche":912.67+454.89,"U-Wert":u_Boden},
			  gfa = 3438.46, volumen=9966.3,
			  anzPersonen=100, stromVerbrauch = 68769)



stromKoeff = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";") #Jahresstromverbrauch bei 1 kWh Verbrauch

class Simulation():
	def __init__(self):		
		#Jedes Teilgebäude wird in einem Dictionary gesammelt
		self.dic_buildings = {"W1":W1,"W2":W2,"W3":W3,"W4":W4,"G1":G1,"G2":G2,"G3":G3,"G4":G4,"S1":S1,"S2":S2}  
		for key,item in self.dic_buildings.items():
			item.InitHeizlast()

		self.heating = True

		self.ta = np.genfromtxt("./Data/climate.csv", delimiter=";", usecols = (1), skip_header = 1)

		self.wwProfile = dict(pd.read_csv("./Data/Warmwasser.csv", decimal=",", sep=";"))

	def InitCoolingPeriod(self):
		pass

	def InitSzenarioWP(self, dic_buildings):
		COP_HZG = 4.5
		COP_WW = 2.8

		speicherHZG_B1 = Speicher(1000)
		WP_HZG_B1 = Wärmepumpe(speicherHZG_B1, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_W1 = Speicher(10000)
		WP_WW_B1 = Wärmepumpe(speicherWW_W1, COP_WW= COP_WW, Pel= 250)

		dic_buildings["W1"].WP_HZG = WP_HZG_B1
		dic_buildings["W1"].WP_WW = WP_WW_B1
		dic_buildings["W1"].DF.InitSzenWP()

		dic_buildings["G1"].WP_HZG = WP_HZG_B1
		dic_buildings["G1"].WP_WW = WP_WW_B1
		dic_buildings["G1"].DF.InitSzenWP()
		#------------------------------------------------------------------------
		speicherHZG_B2 = Speicher(1000)
		WP_HZG_B2 = Wärmepumpe(speicherHZG_B2, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_W2 = Speicher(10000)
		WP_WW_B2 = Wärmepumpe(speicherWW_W2, COP_WW= COP_WW, Pel= 250)

		dic_buildings["W2"].WP_HZG = WP_HZG_B2
		dic_buildings["W2"].WP_WW = WP_WW_B2
		dic_buildings["W2"].DF.InitSzenWP()

		dic_buildings["G2"].WP_HZG = WP_HZG_B2
		dic_buildings["G2"].WP_WW = WP_WW_B2
		dic_buildings["G2"].DF.InitSzenWP()
		#------------------------------------------------------------------------
		speicherHZG_B3 = Speicher(1000)
		WP_HZG_B3 = Wärmepumpe(speicherHZG_B3, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_W3 = Speicher(10000)
		WP_WW_B3 = Wärmepumpe(speicherWW_W3, COP_WW= COP_WW, Pel= 250)

		dic_buildings["W3"].WP_HZG = WP_HZG_B3
		dic_buildings["W3"].WP_WW = WP_WW_B3
		dic_buildings["W3"].DF.InitSzenWP()

		dic_buildings["G3"].WP_HZG = WP_HZG_B3
		dic_buildings["G3"].WP_WW = WP_WW_B3
		dic_buildings["G3"].DF.InitSzenWP()
		#------------------------------------------------------------------------
		speicherHZG_B4 = Speicher(1000)
		WP_HZG_B4 = Wärmepumpe(speicherHZG_B4, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_W4 = Speicher(10000)
		WP_WW_B4 = Wärmepumpe(speicherWW_W4, COP_WW= COP_WW, Pel= 250)

		dic_buildings["W4"].WP_HZG = WP_HZG_B4
		dic_buildings["W4"].WP_WW = WP_WW_B4
		dic_buildings["W4"].DF.InitSzenWP()

		dic_buildings["G4"].WP_HZG = WP_HZG_B4
		dic_buildings["G4"].WP_WW = WP_WW_B4
		dic_buildings["G4"].DF.InitSzenWP()
		#------------------------------------------------------------------------
		speicherHZG_S1 = Speicher(1000)
		WP_HZG_S1 = Wärmepumpe(speicherHZG_S1, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_S1 = Speicher(10000)
		WP_WW_S1 = Wärmepumpe(speicherWW_S1, COP_WW= COP_WW, Pel= 250)

		dic_buildings["S1"].WP_HZG = WP_HZG_S1
		dic_buildings["S1"].WP_WW = WP_WW_S1
		dic_buildings["S1"].DF.InitSzenWP()
		#------------------------------------------------------------------------
		speicherHZG_S2 = Speicher(1000)
		WP_HZG_S2 = Wärmepumpe(speicherHZG_S2, COP_HZG= COP_HZG, Pel= 40)		
		speicherWW_S2 = Speicher(10000)
		WP_WW_S2 = Wärmepumpe(speicherWW_S2, COP_WW= COP_WW, Pel= 250)

		dic_buildings["S2"].WP_HZG = WP_HZG_S2
		dic_buildings["S2"].WP_WW = WP_WW_S2
		dic_buildings["S2"].DF.InitSzenWP()


	def InitSzenarioFW(self):
		pass

	


	def SimWP(self, building, qHLSum):

		qtoTake = building.CalcQtoTargetTemperature(self.heating) * building.gfa / 1000 #kWh
		if qtoTake != 0:
			rest = building.WP_HZG.speicher.SpeicherEntladen(qtoTake, building.WP_HZG.hystEin)
			building.CalcNewTemperature((qtoTake-rest) / building.gfa)
		building.WP_HZG.CheckSpeicher(mode = "HZG")
		building.stromVerbrauchBetrieb += building.WP_HZG.PelBetrieb
		
		print(f"Status WP: {building.WP_HZG.bIsOn}")
		print(f"Innentemperatur: {building.ti} °C")
		print(f"Ladestand Speicher: {round(building.WP_HZG.speicher.Speicherstand(),3)}")
		print("------------------")

	def Simulate(self):
		self.InitSzenarioWP(self.dic_buildings)
		for hour in range(8760):			
			print(f"Stunde: {hour}")

			if DetermineMonth(hour) < 4 or DetermineMonth(hour) > 9:
				self.heating == True
			else:
				self.heating == False

			qHLSum = 0

			for key,building in self.dic_buildings.items():
				
				#if key in ["W2","W3","W4"]:
				#	continue

				building.stromVerbrauchBetrieb = stromKoeff["Wohnen"][hour] * building.stromVerbrauch




				qHLSum = building.CalcThermalFlows(ta=self.ta[hour], hour=hour,
									  anz_Personen=building.anzPersonen, strom = building.stromVerbrauchBetrieb) / 1000
				if building.ti >= 26:
					print("")
				building.CalcNewTemperature(qHLSum)
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






