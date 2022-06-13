# -*- coding: <latin-1> -*-
import pandas as pd
from math import ceil, floor
from random import choice
from Auto import Auto
from miscellaneous import Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
from Backend.Helper import DetermineHourofDay, DetermineDay

import Plotting.DataScraper as DS

from LadeController_Personen import LadeController_Personen

class LadeController(LadeController_Personen):

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
		LadeController_Personen.__init__(self)

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")
		self.anzAutos = anzAutos
		self.li_Autos, checksum = self.InitAutos(anzAutos= anzAutos, distMinLadung= distMinLadung, maxLadung= maxLadung)
		
		self.tooMany = 0
		self.safety = 1.2 #Sicherheitsfaktor in Anteil die auf den Verbrauch aufgeschlagen wird.


	def InitAutos(self,anzAutos, distMinLadung, maxLadung) -> list:
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
			li_Autos.append(Auto(maxLadung= maxLadung, minLadung= minLadung, counter= counter))
			checksum -= 1

		for i in range(int(len(li_Autos)/2)):
			li_Autos[i].bCharging = True

		return li_Autos, checksum
	
	def UpdateLadestand(self, auto, kilometer) -> None:
		"""Nimmt ein 'Auto' und zufallig generierte kilometer um die Ladung zu reduzieren
		auto: auto
			Auto, welches seinen Ladestand reduziert bekommt
		kilometer: float
			Kilometer welches das Auto fahrt"""
		auto.kapazitat -= kilometer * auto.spezVerbrauch
		if auto.kapazitat < 0:
			auto.kapazitat = 0

	def GetChargingCars(self) -> list:
		"""Gibt jedes Auto zuruck, welches gerade an der Ladestation hangt"""
		return [car for car in self.li_Autos if car.bCharging == True]

	def GetAvailableCars(self) -> list:
		"""Gibt liste an Autos zuruck welche entladbar sind"""
		chargingCars = self.GetChargingCars() #first get all charging cars
		return [car for car in chargingCars if car.Speicherstand() > car.minLadung]	

	def CheckTimestep(self, hour, resLast):
		self.CheckPersonsHourly(hour)
		
		li_interCars = []
		li_interPersons = []
		
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
			
		#Autos aus dem Netz auf Mindestladung laden
		self.CheckMinKap()

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

		#Laufvariable der bereits geladenen Energie zurücksetzen
		self.ResetAlreadyLoaded()

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
			
	def PickCar(self, km):
		cars = self.GetChargingCars()
		if not cars:
			return None

		cars.sort(key=lambda x: x.kapazitat, reverse=False)

		demand = km * cars[-1].spezVerbrauch * self.safety

		DS.Scraper.demandDriven += demand / self.safety

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
		car = self.PickCar(km)

		if not car:
			return False

		person.carID = car.ID
		
		
		self.UpdateLadestand(car, km)

		person.status = False
		car.bCharging = False
		return True

	def CheckMinKap(self):
		"""Kontrolliert alle Autos, welche an der Ladestation laden.
		Falls Autos unter der Mindestladegrenze sind, werden diese aus dem Netz geladen"""
		cars = self.GetChargingCars()
		for car in cars:
			if car.kapazitat < car.minLadung * car.maxLadung:
				space = (car.minLadung * car.maxLadung - car.kapazitat)
				toLoad = min([space, car.leistung_MAX, car.alreadyLoaded])
				car.Laden(toLoad)
				DS.Scraper.gridCharging += toLoad

	def ResetAlreadyLoaded(self):
		cars = self.GetChargingCars()
		for car in cars:
			car.alreadyLoaded = car.leistung_MAX