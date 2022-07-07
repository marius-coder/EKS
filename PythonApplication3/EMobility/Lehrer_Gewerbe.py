# -*- coding: cp1252 -*-
from math import ceil
from Auto_Person import Auto
import numpy as np
import pandas as pd
from datetime import datetime

from Ladecontroller_Helper import GenerateNormalNumber,GenerateKilometer


time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

ferien = {
	"Winterferien_Anfang" : ["01.01.2022", "06.01.2022"],
	"Semesterferien" : ["07.02.2022", "13.02.2022"],
	"Sommerferien" : ["02.07.2022", "04.09.2022"],
	"Herbstferien" : ["27.10.2022", "31.10.2022"],
	"Winterferien_Ende" : ["24.12.2022", "31.12.2022"],
	}

#Uhrzeiten (item) zu denen ein Anteil (key) an Personen ankommen
uhrzeitAnkommen = {
	"15" : 6,
	"35" : 7,
	"20" : 8,
	"20" : 9,
	"10" : 10,
	}

#Uhrzeiten (item) zu denen ein Anteil (key) an Personen losfahren
uhrzeitLosfahren = {
	"15" : 15,
	"35" : 16,
	"20" : 17,
	"20" : 18,
	"10" : 19,
	}

def InitZureisende(AutoDaten:dict, maxLadung:float, anzAutos:int, percent:float, bLehrer:bool) -> list:
	"""Initialisiert die zureisenden Personen mit den gew�nschten Attributen
	AutoDaten: dict
		Dicitionary, das die gesammelten AutoDaten enth�lt
	maxLadung: float
		Maximale Ladung der zugereisten Autos
	km: float
		Durchschnittliche Entfernung die die zugereisten Personen zur�cklegen
	anzAutos: int
		Anzahl an Personen/Autos die insgesamt zureisen
	percent: float
		Anteil der zugereisten Personen, die ein E-Autos besitzen mitmachen
	bLehrer:
		Gibt an ob die Person zu einer Bildungseinrichtung geh�rt (Wichtig f�r Ferien)	
		"""
	ret = [] #Halt die finale Liste an Auto Objekten
	anzAutos = ceil(anzAutos*percent/100)
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
			ret.append(Zureisende(AutoDaten= AutoDaten,maxLadung= maxLadung, minLadung= 1, bLehrer= bLehrer,
									  ankommen= uhrzeitAnkommen[percent], losfahren= uhrzeitLosfahren[percent]))
			checksum -= 1

	#Edge-Case Handling (Um Rundungsfehler auszugleichen / Der Fehler sollte immer nur 1 betragen)
	for _ in range(checksum):
		ret.append(Zureisende(AutoDaten= AutoDaten,maxLadung= maxLadung, minLadung= 1, bLehrer= bLehrer,
									  ankommen= uhrzeitAnkommen[percent], losfahren= uhrzeitLosfahren[percent]))
		checksum -= 1

	return ret, checksum


class Zureisende(Auto):

	def __init__(self,AutoDaten, maxLadung, minLadung, ankommen, losfahren, bLehrer= False) -> None:
		Auto.__init__(self, AutoDaten= AutoDaten, minLadung= minLadung)
		self.ankommen = ankommen  #Wann das Auto ankommt
		self.losfahren = losfahren #Wann das Auto losf�hrt
		self.bCharging = False #Autos starten nicht anwesend
		self.bLehrer = bLehrer #Bool ob der Zureisende ein Lehrpersonal ist
		self.maxLadung = maxLadung #Maximale Ladung des Autos in kWh
		self.minLadungAbs = minLadung #Minimale Ladung die eingehalten werden muss in Anteilen
		self.minLadung = self.maxLadung * self.minLadungAbs #Minimale Ladung die eingehalten werden muss in kWh
		self.kapazitat = maxLadung #Laufvariable die die aktuelle Kapazit�t angibt

	def CheckFerien(self, hour:int) -> bool:
		"""Diese Funktion kontrolliert ob sich eine gegebene Stunde innerhalb des Ferienzeitraumes befindet
		hour: int
			Stunde des Jahres"""
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
		"""Simuliert eine Wegstrecke die die zureisenden fahren und passt die Kapazit�t dementsprechend an"""
		km = GenerateKilometer()
		self.kapazitat = self.maxLadung - km * self.spezVerbrauch #Laufvariable in kWh


