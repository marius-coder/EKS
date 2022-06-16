# -*- coding: cp1252 -*-

class Konversionsfaktoren():

	def __init__(self) -> None:
		#Netzstrom
		self.stromnetzPrimärenergie = {
			"Januar" : 1.8,
			"Februar" : 1.79,
			"März" : 1.72,
			"April" : 1.58,
			"Mai" : 1.47,
			"Juni" : 1.46,
			"Juli" : 1.44,
			"August" : 1.48,
			"September" : 1.58,
			"Oktober" : 1.71,
			"November" : 1.77,
			"Dezember" : 1.79,
			}

		self.stromnetzEmissionen = { #kgCO2/kWh
			"Januar" : 0.304,
			"Februar" : 0.304,
			"März" : 0.264,
			"April" : 0.211,
			"Mai" : 0.167,
			"Juni" : 0.163,
			"Juli" : 0.163,
			"August" : 0.167,
			"September" : 0.208,
			"Oktober" : 0.260,
			"November" : 0.282,
			"Dezember" : 0.291,
			}
		self.fernwärmePrimärenergie = 1.6
		self.fernwärmeEmissionen = 59 #kgCO2/kWh

konversionsfaktoren = Konversionsfaktoren()







