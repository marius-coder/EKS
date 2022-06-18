# -*- coding: cp1252 -*-
from numpy import round_
from Auto_Person import Auto, Person
from math import ceil, floor
from Backend.Helper import DetermineHourofDay, DetermineDay
from random import choice, shuffle, seed
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
import Plotting.DataScraper as DS

seed(10)

class LadeController_Personen():
    
	def __init__(self, personenKilometer) -> None:
		self.awayPersons = []
		self.anzPersonen = 1335
		self.percent = 0.3 #Anteil an Personen die beim Mobilitatsprogramm mitmachen
		self.persons = [] #Personen die beim Mobilitätsprogramm mitmachen
		self.basisPersonenKilometer = 5775.77 #Kilometeranzahl die eine Person in einem Jahr mit dem Auto zurücklegt
		self.personenKilometer = personenKilometer
		self.adjustKilometers = personenKilometer / self.basisPersonenKilometer #Faktor um die Kilometer anzahl zu korrigieren
		self.InitPersonen()
		self.drivingPersons = []

	def InitPersonen(self):
		idPerson = 0
		for _ in range(int(self.anzPersonen * self.percent)):
			self.persons.append(Person(idPerson)) #Neue Person mit einer ID generieren

	def FindCarID(self, ID) -> Auto:
		"""sucht Auto in Liste und gibt das gefundene Auto zuruck
		ID: str
			ID des Autos, welches gesucht wird"""
		for car in self.li_Autos:
			if car.ID == ID:
				return car

	def InitDay(self, day) -> list:
		"""InitDay wird einmal am Tag aufgerufen und initialisiert den Tag.
		Dabei werden verschiedene Variablen fur den kommenden tag gesetzt.
		Die Personen, welche an diesen tag mit dem Auto fahren und beim Mobilitatsprogramm
		mitmachen werden ausgewahlt und returned
		day: str
			Typ des Tages
		return: list
			drivingPersons enthalt eine Liste an Personen objekten, welche mit dem Auto fahren"""
		self.anzPers = 0 #Anzahl an Personen die bereits losgefahren sind zurucksetzen
		self.anzPers2 = 0 #Anzahl an Personen die bereits losgefahren sind vom letzten Zeitschritt zurucksetzen
		
		mobilePersons = ceil(CalcMobilePersonen(day, len(self.persons)))
		
		shuffle(self.persons) #Shuffle the person list to equalize km driven
		personsCarSharing = self.persons[0:mobilePersons]
		drivingPersons = []
			
		for person in personsCarSharing:
			person.km = 0
			ways = CalcNumberofWays(day) 
			person.anzAutoWege = CalcAutoWege(ways= ways, day= day)
			if person.anzAutoWege >= 2:
				for _ in range(person.anzAutoWege):
					km = GenerateKilometer()
					person.wegMitAuto += km * self.adjustKilometers #Fur den Verbrauch des Autos
					person.km += km * self.adjustKilometers
				drivingPersons.append(person)
				self.persons.remove(person)

		self.lendrivingPersons = len(drivingPersons)	
		return drivingPersons

	def Control(self, losZahl2, conZahl):
		"""Berechnet die Zahl der Personen, welche in einer Stunde wegfahren/zuruckkommen
		losZahl2: float
			Personenzahl, die fahren/zuruckgekommt (inkl. jetziger Stunde)
		conZahl: float
			Personenzahl, die bereits gefahren/zuruckgekommen sein muss"""
		b = int(round(losZahl2,0))
		r = b - conZahl
		conZahl = b
		return r, conZahl

	def DriveAway(self, person):
		"""Person fahrt weg. Es werden die finalen Kilometer generiert.
		Es wird ein passendes Auto ausgesucht und zugewiesen.
		Person und Auto werden auf abwesend gestellt"""
		km= person.km
		car = self.PickCar(km=km)
		DS.ZV.fahrversuche += 1
		if not car:
			DS.ZV.fehlgeschlageneFahrversuche += 1
			return False

		person.carID = car.ID		
		self.UpdateLadestand(auto= car, kilometer= km)

		person.status = False
		car.bCharging = False
		return True


	def CheckPersonsHourly(self, hour):
		day = DetermineDay(hour)
		hourIndex = DetermineHourofDay(hour)
		if hourIndex == 0:			
			self.drivingPersons.extend(self.InitDay(day)) #Neue Personen generieren und Laufvariablen setzen
			self.tooMany = len(self.awayPersons)
		
		



		#Anzahl an Personen die Losgefahren sollen
		self.anzPers += self.travelData["Losfahren"][hourIndex] / 100 * self.lendrivingPersons

		#Anzahl an Personen die zu dieser Stunde losfahren sollen
		driveAway, self.anzPers2 = self.Control(self.anzPers, self.anzPers2)
		for _ in range(driveAway):			
			person = choice(self.drivingPersons)
			self.drivingPersons.remove(person)			
			if self.DriveAway(person= person):
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
				self.persons.append(person)