
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from random import choices, randint
from Auto import Auto
from PlotMobility import PlotStatusCollection, PlotSample

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
		self.spezVerbrauch = 180 #Wh/km https://ev-database.de/cheatsheet/energy-consumption-electric-car
		mobilityData = pd.read_csv("./Data/Profile_GefahreneKilometer.csv", usecols=[1,3], decimal=",", sep=";")

		self.population = mobilityData["Gefahrene Kilometer"].tolist()
		self.weights = mobilityData["Wahrscheinlichkeit Kilometer gefahren"].tolist()

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")

		self.li_Autos, checksum = self.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= maxLadung)
		self.maxBorrowTime = 24 #Auto kann fur maximal 18 Stunden ausgeborgt werden
		self.averageSpeed = 40 #km/h angenommene Durchschnittsgeschwindigkeit
		self.li_state = [] #Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)

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

		return li_Autos, checksum

	def GenerateKilometer(self):
		"""Gibt eine zufallige Kilometeranzahl zuruck die das Auto gefahren ist.
		Die Zahlen sind custom gewichtet und haben einen Peak bei ca. 48 km"""
		return choices(self.population, self.weights)[0]

	def UpdateLadestand(self, auto, kilometer):
		"""Nimmt ein 'Auto' und zufallig generierte kilometer um die Ladung zu reduzieren"""
		auto.kapazitat -= kilometer * self.spezVerbrauch / 1000
		if auto.kapazitat < 0:
			auto.kapazitat = 0

	def GetChargingCars(self):
		return [car for car in self.li_Autos if car.bCharging == True]

	def DriveAway(self, car, ):
		"""Auto fahrt weg. Es werden Kilometer generiert. 
		Aus den km berechnet sich die mindestzeit die das Auto weg sein wird.
		Speicher des autos wird aktualisiert und abgehangt"""
		km = test.GenerateKilometer()
		self.UpdateLadestand(car, km)
		minTimeAway = round(km/self.averageSpeed+1,0) #Die Zeit die das Auto mindestens weg ist
		car.minTimeAway = minTimeAway 
		car.bCharging = False

	def IterCars(self, hour):
		

		hour = hour%24
		li_inter = []
		for i,car in enumerate(test.li_Autos):
			threshhold = randint(0,100)

			if car.bCharging == True:
				if test.travelData["Losfahren"][hour] > threshhold:
					self.DriveAway(car)

			elif car.bCharging == False and car.minTimeAway == 0:
				car.borrowTime += 1
				if test.travelData["Ankommen"][hour] > threshhold or car.borrowTime > self.maxBorrowTime:
					car.borrowTime = 0
					car.bCharging = True
			li_inter.append(car.bCharging)
		
			car.DecrementMinTimeAway()
		self.li_state.append(li_inter)

	

	def CheckTimestep(self, hour, qLoad, qGeneration):
		#Reslast herausfinden
		#je nach Prioritat Leistungen zuordnen
		#Leistungen nach prioritat abarbeiten
		#Falls rest besteht das Stromnetz einbeziehen (Einspeisung/Bezug)

		resLast = qGeneration - qLoad

		self.IterCars(hour) #Festlegen welche Autos wegfahren bzw. Zuruckkommen

		chargingCars = self.GetChargingCars()

		if resLast > 0:
			for car in chargingCars:
				#Jedes Autos welches läft wird gleich geladen
				#Keine Priorisierung
				car.Laden(resLast/len(chargingCars)) 
			#AufladeFall
			#Autos die da sind aufladen



		elif resLast < 0:
			pass
			#Entladefall

		
distMinLadung = {
	#Key gibt an wie viele Prozent an Autos (Prozent mussen Integer sein)
	#Item gibt die Mindestladung in Anteilen an
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#40% mussen 75% geladen sein
	"30" : 0.5		#50% mussen 50% geladen sein
	}



test = LadeController(anzAutos= 100, distMinLadung= distMinLadung, maxLadung = 75)

for hour in range(200):
	test.CheckTimestep(hour= hour, qLoad= 10, qGeneration= 20)

PlotSample(test.li_state, 10, 192)
PlotStatusCollection(test.li_state)

for _ in range(10):
	for auto in test.li_Autos:
		print(f"Stunde {_}")
		print(f"Aktueller Speicherstand: {auto.Speicherstand()}")
		print(f"Minimaler Speicherstand: {auto.minLadung}")
		kilometer = test.GenerateKilometer()
		print(f"Es wird {kilometer * test.spezVerbrauch / 1000} kWh entladen")
		test.UpdateLadestand(auto= auto, kilometer= kilometer)
		print(f"Aktueller Speicherstand nach Entladen: {auto.Speicherstand()}")
		print("--------------------")
	print("-_-_-_-_-_-_-_-_-_-_-_-_-")

for anzAutos in range(100):
	test = LadeController(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung = 75)
	li_Autos, checksum = test.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= 75)
	if checksum != 0:
		print(f"Fehler bei {anzAutos} Autos")
		print(f"Autos left: {anzAutosMax}")
		print("--------------------")


