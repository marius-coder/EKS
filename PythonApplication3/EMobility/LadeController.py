# -*- coding: <latin-1> -*-
import pandas as pd
import numpy as np
from math import ceil
import matplotlib.pyplot as plt
from random import choice, choices, randint
from Auto import Auto
from PlotMobility import PlotStatusCollection, PlotSample, PlotUseableCapacity
from temp import *
from miscellaneous import DetermineDay, Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
from collections import Counter
from Backend.Helper import DetermineHourofDay

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
		self.maxBorrowTime = 6

		self.li_Autos, checksum = self.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= maxLadung)
		self.averageSpeed = 50 #km/h angenommene Durchschnittsgeschwindigkeit
		self.drivingPersons = []
		self.awayPersons = []


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
		counter = 0

		for percent in keys:
			minLadung = distMinLadung[percent]
			anzInter = int(round(int(percent) * anzAutos / 100 ,0))
			if anzInter == 0 and checksum != 0:
				anzInter = 1
			for _ in range(anzInter):
				if checksum == 0:
					return li_Autos, checksum
				li_Autos.append(Auto(maxLadung= maxLadung, minLadung= minLadung, counter= counter))
				counter += 1
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

	def DriveAway(self, car, person):
		"""Auto fahrt weg. Es werden Kilometer generiert. 
		Aus den km berechnet sich die mindestzeit die das Auto weg sein wird.
		Speicher des autos wird aktualisiert und abgehangt"""
		person.carID = car.ID
		
		km = person.wegMitAuto + person.WaybackHome()
		self.UpdateLadestand(car, km)
		minTimeAway = round(km/self.averageSpeed+1,0) #Die Zeit die das Auto mindestens weg ist
		car.minTimeAway = minTimeAway 
		person.status = False
		car.bCharging = False

	def FindCarID(self, ID):
		for car in self.li_Autos:
			if car.ID == ID:
				return car


	def InitDay(self, day):
		percent = 0.3
		mobilePersons = ceil(CalcMobilePersonen(day, 1335))

		persons = []
		for _ in range(mobilePersons):
			persons.append(Person()) #Neue Person generieren
		
		limit = ceil(mobilePersons * percent)
		personsCarSharing = persons[0:limit]
		drivingPersons = []
			
		for person in personsCarSharing:
			ways = CalcNumberofWays(day) 
			person.anzAutoWege = CalcAutoWege(ways= ways, day= day)
			if person.anzAutoWege >= 2:
				for _ in range(person.anzAutoWege-1):
					km = GenerateKilometer()
					person.AddWay(km) #Fur den Ruckweg
					person.wegMitAuto += km #Fur den Verbrauch des Autos
				drivingPersons.append(person)
		return drivingPersons

	def CheckTimestep(self, hour, qLoad, qGeneration):
		"""Diese Funktion berechnet die Residuallast, entscheidet ob die Autos ge-/entladen werden 
		und ruft die betreffenden Funktionen auf.
		"""
		day = DetermineDay(hour)
		hourIndex = DetermineHourofDay(hour)
		#print(f"Hour: {hour}")
		if hourIndex == 0:
			self.drivingPersons = self.InitDay(day)
			print(f"away Persons: {len(self.awayPersons)}")

		li_inter = []
		for person in self.drivingPersons:
			threshhold = randint(0,100) #Threshhold der bestimmt ob das Auto wegfahrt bzw. zuruckkommt
			if person.status == True:
				if self.travelData["Losfahren"][hourIndex] > threshhold:					
					car = choice(self.GetChargingCars())
					self.DriveAway(car= car, person= person)
					self.awayPersons.append(person)

		for person in self.awayPersons:
			if person.status == False:
				person.borrowTime += 1
				if self.travelData["Ankommen"][hourIndex] > threshhold or person.borrowTime > self.maxBorrowTime:
					person.borrowTime = 0
					car = next((x for x in self.li_Autos if x.ID == person.carID), None)
					person.status = True
					car.bCharging = True
					self.awayPersons.remove(person)
			li_inter.append(person.status)
		
		DS.Scraper.li_state.append(li_inter)
		
		



#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#40% mussen 75% geladen sein
	"30" : 0.5		#50% mussen 50% geladen sein
	}



test = LadeController(anzAutos= 10000, distMinLadung= distMinLadung, maxLadung = 75)

for hour in range(500):
	test.CheckTimestep(hour,10,9)


PlotStatusCollection(DS.Scraper.li_state)