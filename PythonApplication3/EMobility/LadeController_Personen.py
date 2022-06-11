from Auto import Auto
from math import ceil, floor
from miscellaneous import DetermineDay, Person
from Backend.Helper import DetermineHourofDay
from random import choice
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege


class LadeController_Personen():
    
	def __init__(self) -> None:
		self.awayPersons = []

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
		"""Berechnet die Zahl der Personen, welche in einer Stunde wegfahren/zuruckkommen
		losZahl2: float
			Personenzahl, die fahren/zuruckgekommt (inkl. jetziger Stunde)
		conZahl: float
			Personenzahl, die bereits gefahren/zuruckgekommen sein muss"""
		b = int(round(losZahl2,0))
		r = b - conZahl
		conZahl = b
		return r, conZahl




	def CheckPersonsHourly(self, hour):
		day = DetermineDay(hour)
		hourIndex = DetermineHourofDay(hour)
		if hourIndex == 0:			
			self.drivingPersons = self.InitDay(day) #Neue Personen generieren und Laufvariablen setzen
			print(f"Anzahl Leute die gerade weg sind: {len(self.awayPersons)}")
			self.tooMany = len(self.awayPersons)
		
		



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