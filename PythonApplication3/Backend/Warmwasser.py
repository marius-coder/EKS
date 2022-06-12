

import pandas as pd



class WW():
	def __init__(self):
		self.profileWW = pd.read_csv("./Data/Profile_Warmwasser.csv", decimal=",", sep=";")

		self.wwVerbrauch = 40 #Liter/Person und Tag

	def CalcWWEnergy(self, hour, typ):
		return self.anzPersonen * self.profileWW[typ][hour] / 100  * self.wwVerbrauch * 4.180 / 3600 * (60-10)  #60°C WW Temp bei 10 °C KW Temp

