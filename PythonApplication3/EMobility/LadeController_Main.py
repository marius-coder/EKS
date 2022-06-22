# -*- coding: cp1252 -*-
import pandas as pd
from math import ceil, floor
from random import choice, seed, uniform
from Auto_Person import Auto, Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
from Backend.Helper import DetermineHourofDay, DetermineDay
from Lehrer_Gewerbe import InitAu�enstehende
seed(10)

import Plotting.DataScraper as DS

from LadeController_Personen import LadeController_Personen

class LadeController(LadeController_Personen):

	def __init__(self, AutoDaten, distMinLadung, PersonenDaten, infoLehrpersonal= None,infoGewerbepersonal= None):
		"""
		AutoDaten: dict,  
			Dictionary in dem die Autodaten enthalten sind (Anzahl, Verbrauch, Kapazit�t, Effizienz etc.)
		distMinLadung: dict,
			Dictionary welches die Aufteilung der Mindestladestande der E-Autos enthalt
		PersonenDaten: dict
			Dictionary in dem Daten zu den Personen enthalten sind (Anzahl, j�hrliche Personenkilometer, Anteil beim Mobilit�tsprogramm etc.)
		infoLehrpersonal: dict
			Dictionary in dem die Daten zum zureisenden Lehrpersonal enthalten sind (Anzahl, Anteil mitmachende, gefahrene Kilometer, Autokapazit�t etc.)
		infoGewerbepersonal: dict
			Dictionary in dem die Daten zum zureisenden Gewerbepersonal enthalten sind (Anzahl, Anteil mitmachende, gefahrene Kilometer, Autokapazit�t etc.)
		"""	
		LadeController_Personen.__init__(self, PersonenDaten= PersonenDaten)

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")
		
		self.anzAutos = AutoDaten["Anzahl Autos"]
		self.li_Autos, checksum = self.InitAutos(AutoDaten= AutoDaten, distMinLadung= distMinLadung)
		self.Au�enstehende = InitAu�enstehende(AutoDaten= AutoDaten,maxLadung= infoLehrpersonal["Ladung"], percent= infoLehrpersonal["Prozent Mitmachende"]
										,km= infoLehrpersonal["gefahrene km"], anzAutos= infoLehrpersonal["Anzahl"], bLehrer= True)[0]
		self.Au�enstehende.extend(InitAu�enstehende(AutoDaten= AutoDaten,maxLadung= infoGewerbepersonal["Ladung"], percent= infoGewerbepersonal["Prozent Mitmachende"]
											 ,km= infoGewerbepersonal["gefahrene km"], anzAutos= infoGewerbepersonal["Anzahl"], bLehrer= False)[0])
		self.gfa= PersonenDaten["gfa"] #Bruttogeschossfl�che

		self.tooMany = 0 #�berhang an Personen von einem Tag auf den n�chsten
		self.safety = PersonenDaten["Safety"] #Sicherheitsfaktor in Anteil die auf den Verbrauch aufgeschlagen wird.
		self.anteilExterneLadestationen = PersonenDaten["Verbreitung externe Ladestationen"]

	def InitAutos(self,AutoDaten:dict, distMinLadung:dict) -> list:
		"""Initialisiert die Autos mit den angegebenen Mindestladungen
		AutoDaten: dict,  
			Dictionary in dem die Autodaten enthalten sind (Anzahl, Verbrauch, Kapazit�t, Effizienz etc.)
		distMinLadung: dic,
			Dictionary welches die Aufteilung der Mindestladestande enthalt
		li_Autos: list,
			Gibt eine Liste an 'Auto' Objekten zuruck"""

		li_Autos = [] #Halt die finale Liste an Auto Objekten
		checksum = AutoDaten["Anzahl Autos"] #Checksum 
		DS.ZV.maxLadung = AutoDaten["maxLadung"]
		#Keys mussen aufsteigend sortiert sein fur spateres Egde-Case Handling
		keys = sorted(distMinLadung.keys()) 
		counter = 0

		for percent in keys:
			minLadung = distMinLadung[percent] / 100 #Prozent in Anteile wandeln
			anzInter = int(round(int(percent) * AutoDaten["Anzahl Autos"] / 100 ,0))
			if anzInter == 0 and checksum != 0:
				anzInter = 1
			for _ in range(anzInter):
				if checksum == 0:
					return li_Autos, checksum
				li_Autos.append(Auto(AutoDaten, minLadung= minLadung, counter= counter))
				counter += 1
				checksum -= 1

		#Edge-Case Handling (Um Rundungsfehler auszugleichen / Der Fehler sollte immer nur 1 betragen)
		for _ in range(checksum):
			li_Autos.append(Auto(AutoDaten, minLadung= minLadung, counter= counter))
			checksum -= 1

		for i in range(int(len(li_Autos)/2)):
			li_Autos[i].bCharging = True

		return li_Autos, checksum

	def GetChargingCars(self) -> list:
		"""Gibt jedes Auto zuruck, welches gerade an der Ladestation hangt"""
		return [car for car in self.li_Autos if car.bCharging == True]

	def GetAvailableCars(self) -> list:
		"""Gibt liste an Autos zuruck welche entladbar sind"""
		chargingCars = self.GetChargingCars() #first get all charging cars
		return [car for car in chargingCars if car.Speicherstand() > car.minLadungAbs]	

	def GetAu�enstehendeCars(self, hour:int):
		"""Gibt alle anwesenden Autos von zureisenden Personen zur�ck"""
		return [car for car in self.Au�enstehende if car.ankommen <= hour%24 <= car.losfahren]

	def CheckTimestep(self, hour:int, resLast:float):
		"""Checktimestep wird jede Stunde ausgef�hrt und kontrolliert/steuert die notwendigen Events
		hour: int
			Derzeitge Stunde der simulation
		resLast: float
			Residuallast der Stunde (positive Zahlen bedeuten Bedarf>Ertrag)
		"""

		#Mobile Personen berechnen / Personen losfahren und zur�ckkommen managen
		self.CheckPersonsHourly(hour)
		
		if resLast > 0:
			#Autos entladen
			resLastAfterDischarging = self.DischargeCars(resLast)

			if resLast - resLastAfterDischarging < 0:
				raise ValueError("eMobilityDischarge darf nicht negativ sein")
			DS.ZV.eMobilityDischarge[hour] =  resLast - resLastAfterDischarging
			DS.ZV.counterDischarging += 1
		else:
			#Autos laden
			resLast = abs(resLast) #Folgende Funktionen rechnen mit einer positiven zahl			

			cars = self.GetChargingCars() #Es k�nnen nur anwesende Autos laden
			resLastAfterCharging = self.ChargeCars(cars= cars, last= resLast, bTrack= True)
			#Nachdem die Quartiersautos geladen haben, werden die zureisenden geladen
			cars = self.GetAu�enstehendeCars(hour)
			if resLastAfterCharging > 0:
				resLastAfterChargingAu�en = self.ChargeCars(cars= cars, last= resLastAfterCharging)
				DS.zeitVar.LadeLeistungAu�enstehende[hour] = resLastAfterCharging - resLastAfterChargingAu�en

			if resLast - resLastAfterCharging < 0:
				raise ValueError("eMobilityCharge darf nicht negativ sein")
			DS.ZV.eMobilityCharge[hour] =  resLast - resLastAfterCharging			
			DS.ZV.counterCharging += 1

		DS.ZV.resLastAfterDischarging[hour] = DS.ZV.resLastBeforeEMobility[hour] - DS.ZV.eMobilityDischarge[hour]
		DS.ZV.resLastAfterEMobility[hour] = DS.ZV.resLastBeforeEMobility[hour] + DS.ZV.eMobilityCharge[hour]
		#Autos aus dem Netz auf Mindestladung laden
		cars = self.GetChargingCars()
		self.CheckMinKap(cars= cars, bTrack= True)		
		#Autos aus dem Netz auf Mindestladung laden
		cars = self.GetAu�enstehendeCars(hour= hour)
		self.CheckMinKap(cars= cars)		
		#Laufvariable der bereits geladenen Energie zur�cksetzen
		self.ResetAlreadyLoaded()

		statusCars = []
		for car in self.li_Autos:
			if car.bCharging == False:
				statusCars.append("Fahren")
			elif car.kapazitat > car.maxLadung * 0.999:
				statusCars.append("Vollgeladen")
			elif car.kapazitat < car.minLadung:
				statusCars.append("Laden und nicht bereit")
			elif car.kapazitat >= car.minLadung:
				statusCars.append("Laden und bereit")

		if len(statusCars) != len(self.li_Autos):
			raise ValueError("")
		DS.zeitVar.StateofCars.append(statusCars)

	def PickCar(self, km:float):
		"""Funktion die ein passendes Auto aussucht. Dabei wird auf den Bedarf noch ein Sicherheitsfaktor aufgeschlagen
		km: float
			Kilometer welche gefahren werden sollen
		"""

		cars = self.GetChargingCars()
		if not cars: #Falls es keine verf�gbare Autos gibt wird abgebrochen
			return None

		cars.sort(key=lambda x: x.kapazitat, reverse=False) #Autos sortieren nach Kapazit�t

		demand = km * cars[0].spezVerbrauch * self.safety

		if cars[-1].kapazitat < demand: #Falls kein Auto den Bedarf decken kann wird abgebrochen
			return None

		car = next(x for x in cars if x.kapazitat >= demand) #Es wird das Auto gesucht, welche den Bedarf gerade noch decken kann
		return car

	def UpdateLadestand(self, auto:Auto, kilometer:list) -> None:
		"""Nimmt ein 'Auto' und zufallig generierte kilometer um die Ladung zu reduzieren
		auto: Auto
			Auto, welches seinen Ladestand reduziert bekommt
		kilometer: float
			Kilometer welches das Auto fahrt"""
		#Fahrverbrauch tracken
		DS.ZV.verbrauchFahrenEmobilit�t += sum(kilometer) * auto.spezVerbrauch
		DS.ZV.counterDischarging += 1
		

		if self.anteilExterneLadestationen > uniform(0,100):
			driveHome = choice(kilometer) #Es wird ein zuf�lliger Weg als R�ckweg gew�hlt
			kilometer.remove(driveHome)
			auto.kapazitat -= sum(kilometer) * auto.spezVerbrauch #Erste Strecke fahren
			space = auto.kapazitat - auto.maxLadung
			auto.kapazitat = auto.maxLadung #Auto vollladen
			DS.ZV.gridCharging += space
			DS.ZV.counterCharging += 1
			auto.kapazitat -= driveHome * auto.spezVerbrauch #Letzte Strecke fahren
		else:
			auto.kapazitat -= sum(kilometer) * auto.spezVerbrauch


		if auto.kapazitat < 0:
			raise ValueError("Auto hat negative Ladung")

	def ChargeCars(self, cars:list, last:float, bTrack=False):
		"""Diese Funktion k�mmert sich um das Laden der Autos. Es wird dabei nicht mit Netzstrom geladen
		cars: list
			Liste an Auto Objekten, welche geladen werden sollen
		last: float
			Residuallast die in die Autos geladen werden soll
		bTrack: bool
			bool der kontrolliert ob die maximale Ladung getrackt werden soll (das soll nur bei den eigenen Autos passieren)"""
		cars.sort(key=lambda x: x.kapazitat, reverse=True)

		for car in cars:
			if last == 0: #Wenn nichts mehr zu vergeben ist konnen wir fruher abbrechen
				break
			space = car.maxLadung - car.kapazitat
			ladung = min([car.leistung_MAX, last, space]) #Die niedrigste Zahl davon kann geladen werden
			rest = car.Laden(ladung)
			if rest > 0.00001:
				raise ValueError("Ladung ist nicht 0")
			last -= ladung
			if car.kapazitat > car.maxLadung:
				raise ValueError("Auto ist zu voll geladen")
			#Daten Tracken
			if car.kapazitat > DS.ZV.aktuelleLadung and bTrack == True:
				DS.ZV.aktuelleLadung = car.kapazitat
		return last

	def DischargeCars(self, last:float):
		"""Diese Funktion k�mmert sich um das Entladen der Autos um die Geb�udelast abzudecken
		last: float
			Residuallast, welche abgedeckt werden soll
		"""
		cars = self.GetAvailableCars() #Alle Autos die angesteckt sind und die mindestens die Mindestladung haben
		for car in cars:
			car.diff = car.kapazitat - car.minLadung #Potenzielle entladbare Energie berechnen

		cars.sort(key=lambda x: x.diff, reverse= True) #Autos werden nach der gr��ten entladbaren Kapazit�t sortiert
		if cars:
			for car in cars:
				if last == 0: #Wenn die Last abgedeckt werden konnte, konnen wir fr�her abbrechen
					break
				qtoTake = min([car.leistung_MAX, last, car.diff]) #Die niedrigste Zahl davon kann entladen werden
				qtoTake -= car.Entladen(qtoTake)
				last -= qtoTake
				if car.kapazitat < car.minLadung:
					raise ValueError("Auto zu niedrig entladen")

		return last

	def CheckMinKap(self, cars, bTrack= False):
		"""Kontrolliert alle Autos, welche an der Ladestation laden.
		Falls Autos unter der Mindestladegrenze sind, werden diese aus dem Netz geladen"""
		
		for car in cars:
			if car.kapazitat < car.minLadung:
				space = (car.minLadung - car.kapazitat)
				toLoad = min([space, car.leistung_MAX, car.alreadyLoaded])
				car.Laden(toLoad/ car.effizienz)

				if car.kapazitat > car.minLadung:
					raise ValueError("Kapazit�t ist zu Hoch")
				if bTrack:
					DS.ZV.gridCharging += toLoad
					DS.ZV.counterCharging += 1


	def ResetAlreadyLoaded(self):
		"""Hilfsfunktion die eine Laufvariable zur�cksetzt"""
		cars = self.GetChargingCars()
		for car in cars:
			car.alreadyLoaded = car.leistung_MAX