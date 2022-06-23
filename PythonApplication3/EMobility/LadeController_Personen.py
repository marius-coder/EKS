# -*- coding: cp1252 -*-
from numpy import round_
from Auto_Person import Auto, Person
from math import ceil, floor
from Backend.Helper import DetermineHourofDay, DetermineDay
from random import choice, shuffle, seed
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege, GenerateReiseProfil
import Plotting.DataScraper as DS

seed(10)

class LadeController_Personen():
    
	def __init__(self, PersonenDaten) -> None:
		self.awayPersons = []
		self.anzPersonen = PersonenDaten["anzPersonen"]
		self.percent = PersonenDaten["percentMobilität"] / 100 #Anteil an Personen die beim Mobilitatsprogramm mitmachen
		self.persons = [] #Personen die beim Mobilitätsprogramm mitmachen
		self.basisPersonenKilometer = 5775.77 #Kilometeranzahl die eine Person in einem Jahr mit dem Auto zurücklegt
		self.personenKilometer = PersonenDaten["personenKilometer"]
		self.adjustKilometers = self.personenKilometer / self.basisPersonenKilometer #Faktor um die Kilometer anzahl zu korrigieren
		self.InitPersonen()
		self.drivingPersons = []
		self.readytoComeBack = [] #Liste in der die Personen gesammelt werden, die bereit sind zurückzukommen
		self.averageSpeed = 50 #km/h
		self.percentAbweichung = PersonenDaten["percentAbweichung"] / 100 #Prozentwert in Anteile umrechnen

		self.wegfahren = []
		self.ankommen = []

	def InitPersonen(self) -> list:
		"""Initialisiert alle Personen im Quartier, die beim Mibilitätsprogramm mitmachen"""
		for _ in range(int(self.anzPersonen * self.percent)):
			self.persons.append(Person()) #Neue Person mit einer ID generieren

	def FindCarID(self, ID:str) -> Auto:
		"""sucht Auto in Liste und gibt das gefundene Auto zuruck
		ID: str
			ID des Autos, welches gesucht wird"""
		for car in self.li_Autos:
			if car.ID == ID:
				return car

	def InitDay(self, day:str) -> list:
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

		#es können nur Personen wegfahren, die anwesend sind
		personstoPick = [person for person in self.persons if person.status == True]
		personsCarSharing = personstoPick[0:mobilePersons]
		drivingPersons = []
			
		for person in personsCarSharing:
			person.km = []
			ways = CalcNumberofWays(day) 
			person.anzAutoWege = CalcAutoWege(ways= ways, day= day)			

			if person.anzAutoWege >= 2:
				for _ in range(person.anzAutoWege):
					km = GenerateKilometer()
					person.wegMitAuto += km * self.adjustKilometers #Für den Verbrauch des Autos
					person.km.append(km * self.adjustKilometers)
				drivingPersons.append(person)		

		#zugereiste Autos entladen
		for car in self.Außenstehende:
			car.Fahren()

		self.lendrivingPersons = len(drivingPersons)	
		self.tooMany = len(self.readytoComeBack + self.awayPersons)
		self.wegfahren = GenerateReiseProfil(self.travelData["Losfahren"], self.percentAbweichung)
		self.ankommen = GenerateReiseProfil(self.travelData["Ankommen"], self.percentAbweichung)
		return drivingPersons

	def Control(self, losZahl2, conZahl):
		"""Berechnet die Zahl der Personen, welche in einer Stunde wegfahren/zuruckkommen
		losZahl2: float
			Personenzahl, die fahren/zurückgekommt (inkl. jetziger Stunde)
		conZahl: float
			Personenzahl, die bereits gefahren/zurückgekommen sein muss"""
		b = int(round(losZahl2,0))
		r = b - conZahl
		conZahl = b
		return r, conZahl

	def DriveAway(self, person, hour):
		"""Person fahrt weg. Es werden die finalen Kilometer generiert.
		Es wird ein passendes Auto ausgesucht und zugewiesen.
		Person und Auto werden auf abwesend gestellt"""
		km= sum(person.km)
		person.minTimeAway = int(round(km / self.averageSpeed,0))
		car = self.PickCar(km=km)
		DS.ZV.fahrversuche += 1
		if not car:
			DS.ZV.fehlgeschlageneFahrversuche += 1
			return False

		person.carID = car.ID		
		self.UpdateLadestand(auto= car, kilometer= person.km, hour= hour)

		if person.status == False or car.bCharging == False:
			raise TypeError("Person oder Auto sind schon weggefahren")

		person.status = False
		car.bCharging = False
		return True


	def CheckPersonsHourly(self, hour:int):
		"""Setzt jede Stunde alle Personen die losfahren und zurückkommen sollen
		Zu Tagesbeginn werden alle mobile Personen ausgewählt"""
		day = DetermineDay(hour)
		hourIndex = DetermineHourofDay(hour)
		if hourIndex == 0:			
			self.drivingPersons = self.InitDay(day) #Neue Personen generieren und Laufvariablen setzen
			

		#Anzahl an Personen die Losgefahren sollen
		self.anzPers += self.wegfahren[hourIndex] / 100 * self.lendrivingPersons

		#Anzahl an Personen die zu dieser Stunde losfahren sollen
		driveAway, self.anzPers2 = self.Control(self.anzPers, self.anzPers2)
		for _ in range(driveAway):			
			person = choice(self.drivingPersons)
			self.drivingPersons.remove(person)			
			if self.DriveAway(person= person, hour= hour):
				self.awayPersons.append(person)
		

		for person in self.awayPersons[:]:
			if person.minTimeAway == 0:	
				self.readytoComeBack.append(person)
				self.awayPersons.remove(person)
			else:
				person.minTimeAway -= 1

		pers = self.ankommen[hourIndex] / 100 * (self.lendrivingPersons + self.tooMany)
		comingBack, t = self.Control(pers,0)

		for _ in range(comingBack):
			if len(self.readytoComeBack) > 0: #Ask for permission
				person = choice(self.readytoComeBack)
				car = next((x for x in self.li_Autos if x.ID == person.carID), None)
				if car == None:
					raise TypeError("Keine Auto gefunden")
				if person.status == True or car.bCharging == True:
					raise TypeError("Person oder Auto sind schon zurück")
				person.status = True
				car.bCharging = True
				self.readytoComeBack.remove(person)

		statePersons = []
		for person in self.drivingPersons:
			statePersons.append(True)
		for person in self.awayPersons:
			statePersons.append(False)
		for person in self.readytoComeBack:
			statePersons.append(False)

		DS.zeitVar.StateofDrivingPersons.append(statePersons)
				