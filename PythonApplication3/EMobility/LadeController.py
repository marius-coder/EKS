# -*- coding: <latin-1> -*-
import pandas as pd
import numpy as np
from math import ceil, floor
import matplotlib.pyplot as plt
from random import choice
from Auto import Auto
from PlotMobility import PlotStatusCollection, PlotSample, PlotUseableCapacity, PlotSOC, PlotPersonStatus, PlotResiduallast, PlotEigenverbrauch, PlotEigenverbrauchmitAutoeinspeisung, PlotPieDischarge
from temp import *
from miscellaneous import DetermineDay, Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
from collections import Counter
from Backend.Helper import DetermineHourofDay

from Strom.PV import Strombedarf, PV


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
		self.spezVerbrauch = 0.170 #kWh/km https://ev-database.de/cheatsheet/energy-consumption-electric-car

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")
		self.anzPers2 = 0
		self.anzAutos = anzAutos

		self.li_Autos, checksum = self.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= maxLadung)
		self.averageSpeed = 40 #km/h angenommene Durchschnittsgeschwindigkeit
		self.drivingPersons = []
		self.awayPersons = []

		self.tooMany = 0


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
			li_Autos[i].bCharging = True

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



	def FindCarID(self, ID):
		for car in self.li_Autos:
			if car.ID == ID:
				return car


	def InitDay(self, day):
		self.anzPers = 0 #Anzahl an Personen die bereits losgefahren sind zurucksetzen
		self.anzPers2 = 0 #Anzahl an Personen die bereits losgefahren sind vom letzten Zeitschritt zurucksetzen
		percent = 0.3 #Anteil an Personen die beim Mobilitatsprogramm mitmachen
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

		self.lendrivingPersons = len(drivingPersons)	
		return drivingPersons

	def Control(self, losZahl2, conZahl):
		b = int(round(losZahl2,0))
		r = b - conZahl
		conZahl = b
		return r, conZahl

	def CheckTimestep(self, hour, resLast):
		day = DetermineDay(hour)
		hourIndex = DetermineHourofDay(hour)
		if hourIndex == 0:			
			self.drivingPersons = self.InitDay(day) #Neue Personen generieren und Laufvariablen setzen
			print(f"Anzahl Leute die gerade weg sind: {len(self.awayPersons)}")
			self.tooMany = len(self.awayPersons)
		
		

		li_interCars = []
		li_interPersons = []

		#Anzahl an Personen die Losgefahren sollen
		self.anzPers += self.travelData["Losfahren"][hourIndex] / 100 * self.lendrivingPersons

		#Anzahl an Personen die zu dieser Stunde losfahren sollen
		driveAway, self.anzPers2 = self.Control(self.anzPers, self.anzPers2)
		for _ in range(driveAway):			
			person = choice(self.drivingPersons)
			self.drivingPersons.remove(person)			
			self.DriveAway(person= person)
			self.awayPersons.append(person)

		pers = self.travelData["Ankommen"][hourIndex] / 100 * (self.lendrivingPersons + self.tooMany)
		comingBack, t = self.Control(pers,0)

		for _ in range(comingBack):
			if len(self.awayPersons) > 0: #Ask for permission
				person = choice(self.awayPersons)
				car = next((x for x in self.li_Autos if x.ID == person.carID), None)
				person.status = True
				car.bCharging = True
				self.awayPersons.remove(person)

		if resLast > 0:
		#Autos entladen
			#Data Gathering
			resLastAfterDischarging = self.DischargeCars(resLast)
			DS.Scraper.resLastDifferenceAfterDischarge[hour] =  resLast - resLastAfterDischarging
			DS.Scraper.resLastAfterDischarging[hour] = resLastAfterDischarging
		else:
		#Autos laden
			resLast = abs(resLast) #Folgende Funktionen rechnen mit einer positiven zahl			

			#Data Gathering
			resLastAfterCharging = self.ChargeCars(resLast)
			DS.Scraper.resLastAfterCharging[hour] = resLastAfterCharging
			DS.Scraper.resLastDifference[hour] =  resLast - resLastAfterCharging
			
		self.CheckMinKap()

		#print(f"Autos verfugbar: {len(self.GetChargingCars())}")

		#Bookkeeping zum Plotten
		inter = self.drivingPersons.copy()
		inter.extend(self.awayPersons)
		for person in inter:
			li_interPersons.append(person.status)
		for car in self.li_Autos:
			li_interCars.append(car.bCharging)		
		
		
		DS.Scraper.SOC.append(self.GetChargingCars())

		DS.Scraper.li_state.append(li_interPersons)
		DS.Scraper.li_stateCars.append(li_interCars)

	def ChargeCars(self, last):
		cars = self.GetChargingCars()
		cars.sort(key=lambda x: x.kapazitat, reverse=True)

		for car in cars:
			if last == 0: #Wenn nichts mehr zu vergeben ist konnen wir fruher abbrechen
				break
			space = car.maxLadung - car.kapazitat
			ladung = min([car.leistung_MAX, last, space]) #Die niedrigste Zahl davon kann geladen werden
			car.Laden(ladung)
			last -= ladung
		return last

	def DischargeCars(self, last):
		cars = self.GetAvailableCars() #Alle Autos die angesteckt sind und die mindestens die Mindestladung haben
		for car in cars:
			car.diff = car.kapazitat - car.maxLadung * car.minLadung

		cars.sort(key=lambda x: x.diff, reverse= True)
		if cars:
			for car in cars:
				if last == 0: #Wenn die Last abgedeckt werden konnte, konnen wir fruher abbrechen
					break
				qtoTake = min([car.leistung_MAX, last, car.diff]) #Die niedrigste Zahl davon kann entladen werden
				qtoTake -= car.Entladen(qtoTake)
				last -= qtoTake
		return last
			
	def PickCar(self, demand):
		safety = 1.1
		demand = demand * safety

		cars = self.GetChargingCars()
		cars.sort(key=lambda x: x.kapazitat, reverse=False)

		if cars[-1].kapazitat < demand:
			return cars[-1]

		car = next(x for x in cars if x.kapazitat >= demand)
		#print(f"Best Choice: {car.kapazitat}")
		return car

	def DriveAway(self, person):
		"""Person fahrt weg. Es werden die finalen Kilometer generiert.
		Es wird ein passendes Auto ausgesucht und zugewiesen.
		Person und Auto werden auf abwesend gestellt"""
		km = person.wegMitAuto + person.WaybackHome()
		car = self.PickCar(km * self.spezVerbrauch)

		person.carID = car.ID
		
		
		self.UpdateLadestand(car, km)
		minTimeAway = round(km/self.averageSpeed+1,0) #Die Zeit die das Auto mindestens weg ist
		car.minTimeAway = minTimeAway 
		person.status = False
		car.bCharging = False

	def CheckMinKap(self):
		cars = self.GetChargingCars()
		for car in cars:
			if car.kapazitat < car.minLadung * car.maxLadung:
				toLoad = (car.minLadung * car.maxLadung - car.kapazitat)
				car.Laden(toLoad)

#Key gibt an wie viele Prozent an Autos (Prozent mussen ganze Zahlen sein)
#Item gibt die Mindestladung in Anteilen an	
distMinLadung = {
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#60% mussen 75% geladen sein
	"30" : 0.5		#30% mussen 50% geladen sein
	}



Control = LadeController(anzAutos= 120, distMinLadung= distMinLadung, maxLadung = 41)

for hour in range(8760):

	pv = PV[hour]
	bedarf = Strombedarf["Wohnen"][hour] + Strombedarf["Gewerbe"][hour] + Strombedarf["Schule"][hour]
	
	#resLast = 1 - pv
	resLast = bedarf - pv
	DS.Scraper.resLast.append(resLast)
	#print(f"Stunde: {hour}")
	#print(f"Residuallast: {resLast} kWh")
	Control.CheckTimestep(hour= hour,resLast= resLast)



PlotPieDischarge(sum(DS.Scraper.resLastDifferenceAfterDischarge), sum(DS.Scraper.resLastDifference), Control.li_Autos[0])
PlotEigenverbrauchmitAutoeinspeisung(PV,DS.Scraper.resLast, DS.Scraper.resLastDifference)

PlotEigenverbrauch(PV,DS.Scraper.resLast)
PlotResiduallast(PV,Strombedarf["Wohnen"].tolist(),DS.Scraper.resLast)
PlotPersonStatus(DS.Scraper.li_state)
PlotStatusCollection(DS.Scraper.li_stateCars)
#PlotSOC(DS.Scraper.SOC, anzAuto= Control.anzAutos)


