
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
		self.maxBorrowTime = 24 #Auto kann fur maximal 24 Stunden ausgeborgt werden
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

		for i in range(int(len(li_Autos)/2)):
			li_Autos[i].bCharging = False

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

	def GetChargingCars(self) -> list:
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

	def IterCars(self, hour, iterations):
		"""Iteriert durch die Autos und entscheidet ob die Autos wegfahren bzw. Ankommen
		iterations: int
			Bestimmt wie oft der threshhold getestet wird. Je mehr iterations desto hoher werden die Extremwerte"""

		hour = hour%24
		li_inter = []
		for car in test.li_Autos:
			for _ in range(iterations):
				threshhold = randint(0,100) #Threshhold der bestimmt ob das Auto wegfahrt bzw. zuruckkommt

				if car.bCharging == True: #Nur wenn das Auto da ist kann es wegfahren
					if test.travelData["Losfahren"][hour] > threshhold:
						self.DriveAway(car)
			
				#Nur wenn das Auto die Mindestzeit weg war kann es zuruckkommen
				elif car.bCharging == False and car.minTimeAway == 0: 
					car.borrowTime += 1
					#Es gibt eine maximal ausborgezeit (um Wahrscheinlichkeiten zu verhindern dass ein Auto zu lange weg ist)
					if test.travelData["Ankommen"][hour] > threshhold or car.borrowTime > self.maxBorrowTime:
						car.borrowTime = 0
						car.bCharging = True
			li_inter.append(car.bCharging) #Datensammlung fur spateres plotting
		
			car.DecrementMinTimeAway()
		self.li_state.append(li_inter)
			
	def ResetLoadParameter(self):
		"""Nach jeden Zeitschritt muss die loaded Variable wieder zuruckgesetzt werden.
		loaded beschreibt wie viel Energie bereits in das Auto geladen wurde in einem Zeitschritt"""
		for car in self.li_Autos:
			car.loaded = car.leistung_MAX #Laufvariablen zurucksetzen

	def GetAvailableCars(self) -> list:
		"""Gibt liste an Autos zuruck welche entladbar sind"""
		chargingCars = self.GetChargingCars() #first get all charging cars
		return [car for car in chargingCars if car.Speicherstand() > car.minLadung]

	def LoadCars(self, resLast):
		"""Diese Funktion ladt die Autos auf. dabei wird keine priorisierung in der Ladereihenfolge vorgenommen.
		Alle Autos werden nach moglichkeit gleichmasig geladen"""

		chargingCars = self.GetChargingCars()
		#Theoretische Ladung pro Auto berechnen
		length = len(chargingCars)
		if length == 0:
			length = 1		
		ladungTheoretisch = resLast / length
		for car in chargingCars:
			ladeplatzAuto = car.maxLadung - car.kapazitat
			#Es kann nur das Minimum dieser Werte geladen werden 
			#(nicht genug ladeenergie, nicht genug Speicherplatz, Uberschreitung der Ladeleistung, bereits zu viel geladen)
			ladung = min([ladungTheoretisch,ladeplatzAuto,car.leistung_MAX,car.loaded])
			car.loaded -= ladung #Laufvariable wird abgezogen
			check = car.Laden(ladung) #Auto aufladen
			if check != 0: #Sanity Ceck, das sollte nie zutreffen
				print("")
			resLast -= ladung
		return resLast

	def DeloadCars(self, resLast):		
		availableCars = self.GetAvailableCars() #Alle Autos die angesteckt sind und die genugend Ladung haben
		#Theoretische Ladung pro Auto berechnen
		length = len(availableCars)
		if length == 0:
			length = 1		
		ladungTheoretisch = resLast / length

		for car in availableCars:
			ladeKapAuto = car.kapazitat - car.kapazitat * car.minLadung
			#Es kann nur das Minimum dieser Werte geladen werden 
			#(nicht genug ladeenergie, nicht genug Speicherplatz, Uberschreitung der Ladeleistung, bereits zu viel geladen)
			ladung = min([ladungTheoretisch,ladeKapAuto,car.leistung_MAX,car.loaded])
			car.loaded -= ladung #Laufvariable wird abgezogen
			check = car.Entladen(ladung) #Auto aufladen
			if check != 0: #Sanity Ceck, das sollte nie zutreffen
				print("")
			resLast -= ladung
		return resLast

	def CheckCars(self):
		cars = self.GetChargingCars()
		for car in cars:
			if car.Speicherstand() > car.minLadung:
				raise ValueError('Cars capacity is too low')

	def CheckTimestep(self, hour, qLoad, qGeneration):
		"""Diese Funktion berechnet die Residuallast, entscheidet ob die Autos ge-/entladen werden 
		und ruft die betreffenden Funktionen auf.
		"""
		#Reslast herausfinden
		#je nach Prioritat Leistungen zuordnen
		#Leistungen nach prioritat abarbeiten
		#Falls rest besteht das Stromnetz einbeziehen (Einspeisung/Bezug)

		self.IterCars(hour= hour, iterations= 1) #Festlegen welche Autos wegfahren bzw. Zuruckkommen
		
		resLast = qGeneration - qLoad
		if resLast > 0:			
		#Ladefall
			for _ in range(3):
				#Der Ladevorgang wird drei mal iteriert, wenn danach noch resLast ubrig ist wird diese weiter verwendet
				resLast = self.LoadCars(resLast= resLast)
				if resLast == 0: #Wenn resLast bereits 0 ist konnen wir vorzeitig abbrechen
					break
			self.ResetLoadParameter()
		
		elif resLast < 0:
		#Entladefall
			for _ in range(3):
				#Der Ladevorgang wird drei mal iteriert, wenn danach noch resLast ubrig ist wird diese weiter verwendet
				resLast = self.DeloadCars(resLast= abs(resLast))
				if resLast == 0: #Wenn resLast bereits 0 ist konnen wir vorzeitig abbrechen
					break
			self.ResetLoadParameter()
			

		
distMinLadung = {
	#Key gibt an wie viele Prozent an Autos (Prozent mussen Integer sein)
	#Item gibt die Mindestladung in Anteilen an
	"10" : 1,		#10% mussen voll geladen sein
	"60" : 0.75,	#40% mussen 75% geladen sein
	"30" : 0.5		#50% mussen 50% geladen sein
	}



test = LadeController(anzAutos= 100, distMinLadung= distMinLadung, maxLadung = 75)

for hour in range(128):
	test.CheckTimestep(hour= hour, qLoad= 20, qGeneration= 10)

PlotSample(test.li_state, 10, 128)
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


