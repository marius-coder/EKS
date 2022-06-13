

import pandas as pd



class WW():
	def __init__(self):
		self.profileWW = pd.read_csv("./Data/Profile_Warmwasser.csv", decimal=",", sep=";")

		self.wwVerbrauchWohnen = 40 #Liter/Person und Tag
		self.wwVerbrauchGewerbe = 25 #Liter/Person und Tag

	def CalcWWEnergyWohnen(self, hour, typ):
		return self.anzPersonen * self.profileWW[typ][hour%24] / 100  * self.wwVerbrauchWohnen * 4.180 / 3600 * (60-10)  #60°C WW Temp bei 10 °C KW Temp

	def CalcWWEnergyGewerbe(self, hour, typ):
		typ = "Gewerbe_"+typ
		return self.anzPersonen * self.profileWW[typ][hour%24] / 100  * self.wwVerbrauchGewerbe * 4.180 / 3600 * (60-10)  #60°C WW Temp bei 10 °C KW Temp



