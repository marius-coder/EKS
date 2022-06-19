# -*- coding: cp1252 -*-
from Auto_Person import Auto
import numpy as np
import pandas as pd
from datetime import datetime

from Ladecontroller_Helper import GenerateNormalNumber


time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

ferien = {
	"Winterferien_Anfang" : ["01.01.2022", "06.01.2022"],
	"Semesterferien" : ["07.02.2022", "13.02.2022"],
	"Sommerferien" : ["02.07.2022", "04.09.2022"],
	"Herbstferien" : ["27.10.2022", "31.10.2022"],
	"Winterferien_Ende" : ["24.12.2022", "31.12.2022"],
	}

uhrzeitAnkommen = {
	"15" : 6,
	"35" : 7,
	"20" : 8,
	"20" : 9,
	"10" : 10,
	}

uhrzeitLosfahren = {
	"15" : 15,
	"35" : 16,
	"20" : 17,
	"20" : 18,
	"10" : 19,
	}




def InitAußenstehende(maxLadung, km, anzAutos, bLehrer) -> list:
	ret = [] #Halt die finale Liste an Auto Objekten
	checksum = anzAutos #Checksum 
	#Keys mussen aufsteigend sortiert sein fur spateres Egde-Case Handling
	keys = uhrzeitAnkommen.keys()

	for percent in keys:
		anzInter = int(round(int(percent) * anzAutos / 100 ,0))
		if anzInter == 0 and checksum != 0:
			anzInter = 1
		for _ in range(anzInter):
			if checksum == 0:
				return ret, checksum
			ret.append(Außenstehende(maxLadung= maxLadung, minLadung= 1, km= km, bLehrer= bLehrer,
									  ankommen= uhrzeitAnkommen[percent], losfahren= uhrzeitLosfahren[percent]))
			checksum -= 1

	#Edge-Case Handling (Um Rundungsfehler auszugleichen / Der Fehler sollte immer nur 1 betragen)
	for _ in range(checksum):
		ret.append(Außenstehende(maxLadung= maxLadung, minLadung= 1, km= km, bLehrer= bLehrer,
									  ankommen= uhrzeitAnkommen[percent], losfahren= uhrzeitLosfahren[percent]))
		checksum -= 1

	return ret, checksum


class Außenstehende(Auto):

	def __init__(self, km, maxLadung, minLadung, ankommen, losfahren, bLehrer= False) -> None:
		Auto.__init__(self, maxLadung= maxLadung, minLadung= minLadung)
		self.km = km
		self.ankommen = ankommen  #Wann das Auto ankommt
		self.losfahren = losfahren #Wann das Auto losfährt
		self.bCharging = False
		self.bLehrer = bLehrer
		self.maxLadung = maxLadung
		self.minLadung = minLadung
		self.kapazitat = maxLadung

	def CheckFerien(self, hour):
		datum = time[hour]
		date_format = "%d.%m.%Y"
		ret = []
		for start,end in ferien.values():			
			if datetime.strptime(start, date_format) <= datum <= datetime.strptime(end, date_format):
				ret.append(True)
			else:
				ret.append(False)
		if any(ret):
			return True
		else:
			return False

	def Fahren(self):
		std = self.km * 0.15
		val = GenerateNormalNumber(self.km, std)
		self.kapazitat = self.maxLadung - val * self.spezVerbrauch #Laufvariable in kWh


