
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from random import choices, randint
from Auto import Auto
from PlotMobility import PlotStatusCollection, PlotSample, PlotUseableCapacity
from temp import *
from miscellaneous import DetermineDay, Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateIfDriving,GenerateKilometer

import Plotting.DataScraper as DS

class LadeController():

	def __init__(self, anzAutos, distMinLadung, maxLadung):
		"""Die Anzahl an Autos und die prozentuale Aufteilung sollte am besten keine Kommazahlen ergeben
		anzAutos: int,  
			Anzahl an Autos die der Controller managed 
		distMinLadung: dic,
			Dictionary welches die Aufteilung der Mindestladestande enthalt
		maxLadung: int,
			Maximale Ladekapazitat der Autos. 
			Es wird davon ausgegangen dass nur baugleiche Autos verwendet werden.
			Eingabe in kWh.
		"""		
		self.spezVerbrauch = 170 #Wh/km https://ev-database.de/cheatsheet/energy-consumption-electric-car
		mobilityData = pd.read_csv("./Data/Profile_GefahreneKilometer.csv", usecols=[1,3], decimal=",", sep=";")

		self.population = mobilityData["Gefahrene Kilometer"].tolist()
		self.weights = mobilityData["Wahrscheinlichkeit Kilometer gefahren"].tolist()

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")

		self.li_Autos, checksum = self.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= maxLadung)
		self.averageSpeed = 50 #km/h angenommene Durchschnittsgeschwindigkeit


	def InitAutos(self,anzAutos, distMinLadung, maxLadung):
		"""Initialisiert die Autos mit den angegebenen Mindestladungen
		anzAutos: int,  
			Anzahl an Autos die der Controller managed 
		distMinLadung: dic,
			Dictionary welches die Aufteilung der Mindestladestande enthalt
		maxLadung: int,
			Maximale Ladekapazitat der Autos. 
			Es wird davon ausgegangen dass nur baugleiche Autos verwendet werden.
			Eingabe in kWh.
		li_Autos: list,
			Gibt eine Liste an 'Auto' Objekten zuruck"""

		li_Autos = [] #Halt die finale Liste an Auto Objekten
		checksum = anzAutos #Checksum 

		#Keys mussen aufsteigend sortiert sein fur spateres Egde-Case Handling
		keys = sorted(distMinLadung.keys()) 

		for percent in keys:
			minLadung = distMinLadung[percent]
			anzInter = int(round(int(percent) * anzAutos / 100 ,0))
			if anzInter == 0 and checksum != 0:
				anzInter = 1
			for _ in range(anzInter):
				if checksum == 0:
					return li_Autos, checksum
				li_Autos.append(Auto(maxLadung= maxLadung, minLadung= minLadung))
				checksum -= 1

		#Edge-Case Handling (Um Rundungsfehler auszugleichen / Der Fehler sollte immer nur 1 betragen)
		for _ in range(checksum):
			li_Autos.append(Auto(maxLadung= maxLadung, minLadung= minLadung))
			checksum -= 1

		for i in range(int(len(li_Autos)/2)):
			li_Autos[i].bCharging = False

		return li_Autos, checksum
	
	def UpdateLadestand(self, auto, kilometer):
		"""Nimmt ein 'Auto' und zufallig generierte kilometer um die Ladung zu reduzieren"""
		auto.kapazitat -= kilometer * self.spezVerbrauch / 1000
		if auto.kapazitat < 0:
			auto.kapazitat = 0

	def GetChargingCars(self) -> list:
		return [car for car in self.li_Autos if car.bCharging == True]

	def GetAvailableCars(self) -> list:
		"""Gibt liste an Autos zuruck welche entladbar sind"""
		chargingCars = self.GetChargingCars() #first get all charging cars
		return [car for car in chargingCars if car.Speicherstand() > car.minLadung]

	def GetUseableCapacity(self):
		chargingCars = self.GetChargingCars()	#Alle Autos die angesteckt sind
		availableCars = self.GetAvailableCars() #Alle Autos die angesteckt sind und die genugend Ladung haben

		useableCapacity = 0
		for car in availableCars:
			useableCapacity += car.kapazitat - car.kapazitat * car.minLadung
		return useableCapacity

	def CheckTimestep(self, hour, qLoad, qGeneration):
		"""Diese Funktion berechnet die Residuallast, entscheidet ob die Autos ge-/entladen werden 
		und ruft die betreffenden Funktionen auf.
		"""
		day = DetermineDay(hour)

		mobilePersons = CalcMobilePersonen(1335)
		li_Persons = []
		for _ in mobilePersons:
			person = Person() #Neue Person generieren
			ways = CalcNumberofWays(day) -1 #Ein weg ist immer für den Nachhauseweg reserviert
			if ways > 1:
				for _ in range(ways):
					zweck = GenerateWegZweck(day)
					if GenerateIfDriving(zweck) == "AutolenkerIn":
						weg = GenerateKilometer()
						person.wegMitAuto += weg
					else:
						weg = GenerateKilometer()
					person.wegGesamt += weg
					person.AddWay(weg)
						#Weg wird nicht mit auto zurückgelegt
		,,GenerateIfDriving,GenerateKilometer


#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#40% mussen 75% geladen sein
	"30" : 0.5		#50% mussen 50% geladen sein
	}



test = LadeController(anzAutos= 100, distMinLadung= distMinLadung, maxLadung = 75)

for hour in range(500):
	test.CheckTimestep(hour,10,9)


