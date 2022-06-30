# -*- coding: cp1252 -*-
import pandas as pd
from math import ceil, floor
from random import choice, seed, uniform
from Auto_Person import Auto, Person
from Ladecontroller_Helper import CalcMobilePersonen,CalcNumberofWays,GenerateWegZweck,GenerateTransportmittel,GenerateKilometer,CalcAutoWege
from Backend.Helper import DetermineHourofDay, DetermineDay
from Lehrer_Gewerbe import InitAußenstehende
seed(10)

import Plotting.DataScraper as DS

from LadeController_Personen import LadeController_Personen

class LadeController(LadeController_Personen):

	def __init__(self, AutoDaten, distMinLadung, PersonenDaten, infoLehrpersonal= None,infoGewerbepersonal= None):
		"""
		AutoDaten: dict,  
			Dictionary in dem die Autodaten enthalten sind (Anzahl, Verbrauch, Kapazität, Effizienz etc.)
		distMinLadung: dict,
			Dictionary welches die Aufteilung der Mindestladestande der E-Autos enthalt
		PersonenDaten: dict
			Dictionary in dem Daten zu den Personen enthalten sind (Anzahl, jährliche Personenkilometer, Anteil beim Mobilitätsprogramm etc.)
		infoLehrpersonal: dict
			Dictionary in dem die Daten zum zureisenden Lehrpersonal enthalten sind (Anzahl, Anteil mitmachende, gefahrene Kilometer, Autokapazität etc.)
		infoGewerbepersonal: dict
			Dictionary in dem die Daten zum zureisenden Gewerbepersonal enthalten sind (Anzahl, Anteil mitmachende, gefahrene Kilometer, Autokapazität etc.)
		"""	
		LadeController_Personen.__init__(self, PersonenDaten= PersonenDaten)

		self.travelData = pd.read_csv("./Data/Profile_Travel.csv", usecols=[1,2,3,4], decimal=",", sep=";")
		
		self.anzAutos = AutoDaten["Anzahl Autos"]
		self.li_Autos, checksum = self.InitAutos(AutoDaten= AutoDaten, distMinLadung= distMinLadung)
		self.Außenstehende = InitAußenstehende(AutoDaten= AutoDaten,maxLadung= infoLehrpersonal["Ladung"], percent= infoLehrpersonal["Prozent Mitmachende"]
										, anzAutos= infoLehrpersonal["Anzahl"], bLehrer= True)[0]
		self.Außenstehende.extend(InitAußenstehende(AutoDaten= AutoDaten,maxLadung= infoGewerbepersonal["Ladung"], percent= infoGewerbepersonal["Prozent Mitmachende"]
											 , anzAutos= infoGewerbepersonal["Anzahl"], bLehrer= False)[0])
		self.gfa= PersonenDaten["gfa"] #Bruttogeschossfläche

		self.tooMany = 0 #Überhang an Personen von einem Tag auf den nächsten
		self.safety = PersonenDaten["Safety"] #Sicherheitsfaktor in Anteil die auf den Verbrauch aufgeschlagen wird.
		self.anteilExterneLadestationen = PersonenDaten["Verbreitung externe Ladestationen"]

	def InitAutos(self,AutoDaten:dict, distMinLadung:dict) -> list:
		"""Initialisiert die Autos mit den angegebenen Mindestladungen
		AutoDaten: dict,  
			Dictionary in dem die Autodaten enthalten sind (Anzahl, Verbrauch, Kapazität, Effizienz etc.)
		distMinLadung: dic,
			Dictionary welches die Aufteilung der Mindestladestande enthalt
		li_Autos: list,
			Gibt eine Liste an 'Auto' Objekten zuruck"""

		li_Autos = [] #Halt die finale Liste an Auto Objekten
		checksum = AutoDaten["Anzahl Autos"] #Checksum 
		DS.ZV.maxLadung = AutoDaten["maxLadung"]
		#Keys mussen aufsteigend sortiert sein fur spateres Egde-Case Handling
		sortedMinLadung = dict(sorted(distMinLadung.items(), key=lambda item: item[1]))
		counter = 0

		for minLadung, percent in sortedMinLadung.items():
			minLadung = int(minLadung)/100
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
			counter += 1
			checksum -= 1

		for i in range(int(len(li_Autos)/2)):
			li_Autos[i].bCharging = True
		if counter != AutoDaten["Anzahl Autos"]:
			raise ValueError("ID Stimmt nicht")
		return li_Autos, checksum

	def GetChargingCars(self) -> list:
		"""Gibt jedes Auto zuruck, welches gerade an der Ladestation hangt"""
		return [car for car in self.li_Autos if car.bCharging == True]

	#def GetAvailableCars(self) -> list:
	#	"""Gibt liste an Autos zuruck welche entladbar sind"""
	#	chargingCars = self.GetChargingCars() #first get all charging cars
	#	return [car for car in chargingCars if car.Speicherstand() > car.minLadungAbs]	

	def GetAußenstehendeCars(self, hour:int):
		"""Gibt alle anwesenden Autos von zureisenden Personen zurück"""
		return [car for car in self.Außenstehende if car.ankommen <= hour%24 <= car.losfahren]

	def CheckTimestep(self, hour:int, resLast:float):
		"""Checktimestep wird jede Stunde ausgeführt und kontrolliert/steuert die notwendigen Events
		hour: int
			Derzeitge Stunde der simulation
		resLast: float
			Residuallast der Stunde (positive Zahlen bedeuten Bedarf>Ertrag)
		"""

		#Mobile Personen berechnen / Personen losfahren und zurückkommen managen
		self.CheckPersonsHourly(hour)
		
		if resLast > 0:
			#Autos entladen
			resLastAfterDischarging, entladungEMobility = self.DischargeCars(resLast)

			if resLast - resLastAfterDischarging < 0:
				raise ValueError("eMobilityDischarge darf nicht negativ sein")
			self.CalcFahrverbrauch(demand= entladungEMobility,hour= hour, demandType= "Entladung")
			DS.zeitVar.eMobilityDischarge[hour] =  entladungEMobility
			DS.zeitVar.buildingDemandHourly[hour] += entladungEMobility
		else:
			#Autos laden

			cars = self.GetChargingCars() #Es können nur anwesende Autos laden
			resLastAfterCharging, ladungEMobility = self.ChargeCars(cars= cars, last= abs(resLast), bTrack= True)
			DS.zeitVar.eMobilityCharge[hour] = ladungEMobility	
			DS.zeitVar.pvChargingHourly[hour] += ladungEMobility
			DS.ZV.emobilitätErneuerbarGeladen += ladungEMobility
			#Nachdem die Quartiersautos geladen haben, werden die zureisenden geladen
			cars = self.GetAußenstehendeCars(hour)
			if resLastAfterCharging > 0:
				resLastAfterChargingZureisende, ladungZureisende  = self.ChargeCars(cars= cars, last= resLastAfterCharging)
				DS.zeitVar.LadeLeistungAußenstehende[hour] = ladungZureisende

				
			if abs(resLast) - resLastAfterCharging < 0:
				raise ValueError("eMobilityCharge darf nicht negativ sein")
			
		DS.zeitVar.resLastAfterEMobility[hour] = resLast - DS.zeitVar.eMobilityDischarge[hour] + DS.zeitVar.eMobilityCharge[hour] 
		DS.zeitVar.resLastAfterZureisende[hour] = DS.zeitVar.resLastAfterEMobility[hour] + DS.zeitVar.LadeLeistungAußenstehende[hour]
		
		#Autos aus dem Netz auf Mindestladung laden
		cars = self.GetChargingCars()
		self.CheckMinKap(cars= cars, hour= hour, bTrack= True)		
		#Autos aus dem Netz auf Mindestladung laden
		cars = self.GetAußenstehendeCars(hour= hour)
		self.CheckMinKap(cars= cars, hour= hour,)		
		#Laufvariable der bereits geladenen Energie zurücksetzen
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
		self.CalcUngenutzterSpeicherplatz(hour)

	def PickCar(self, km:float):
		"""Funktion die ein passendes Auto aussucht. Dabei wird auf den Bedarf noch ein Sicherheitsfaktor aufgeschlagen
		km: float
			Kilometer welche gefahren werden sollen
		"""

		cars = self.GetChargingCars()
		cars = [car for car in cars if car.bCharging == True]
		if not cars: #Falls es keine verfügbare Autos gibt wird abgebrochen
			return None

		cars.sort(key=lambda x: x.kapazitat, reverse=False) #Autos sortieren nach Kapazität

		demand = km * cars[0].spezVerbrauch * self.safety

		if cars[-1].kapazitat < demand: #Falls kein Auto den Bedarf decken kann wird abgebrochen
			return None

		car = next(x for x in cars if x.kapazitat >= demand) #Es wird das Auto gesucht, welche den Bedarf gerade noch decken kann
		return car

	def CalcFahrverbrauch(self, demand, hour, demandType):
		factorErneuerbar = DS.ZV.emobilitätErneuerbarGeladen / (DS.ZV.emobilitätErneuerbarGeladen + DS.ZV.emobilitätNetzGeladen)
		factorNetz = DS.ZV.emobilitätNetzGeladen / (DS.ZV.emobilitätErneuerbarGeladen + DS.ZV.emobilitätNetzGeladen)

		entladungErn = factorErneuerbar * demand
		entladungNetz = factorNetz * demand
		DS.ZV.emobilitätErneuerbarGeladen -= entladungErn
		DS.ZV.emobilitätNetzGeladen -= entladungNetz

		if DS.ZV.emobilitätErneuerbarGeladen < 0 or DS.ZV.emobilitätNetzGeladen < 0:
			raise ValueError("EmobilitätLadung unter Null")

		if demandType == "Fahren":
			DS.zeitVar.fahrverbrauchLokal[hour] += entladungErn
			DS.zeitVar.fahrverbrauchNetz[hour] += entladungNetz
		elif demandType == "Entladung":
			DS.zeitVar.entladungLokal[hour] += entladungErn
			DS.zeitVar.entladungNetz[hour] += entladungNetz
		
		

	def UpdateLadestand(self, auto:Auto, kilometer:list, hour:int) -> None:
		"""Nimmt ein 'Auto' und zufallig generierte kilometer um die Ladung zu reduzieren
		auto: Auto
			Auto, welches seinen Ladestand reduziert bekommt
		kilometer: float
			Kilometer welches das Auto fahrt
		hour: int
			Stunde des Jahres
			"""
		#Fahrverbrauch tracken
		demand = sum(kilometer) * auto.spezVerbrauch	
		DS.ZV.verbrauchFahrenEmobilität += demand
		DS.zeitVar.carDemandHourly[hour] += demand
		if self.anteilExterneLadestationen > uniform(0,99):
			driveHome = choice(kilometer) #Es wird ein zufälliger Weg als Rückweg gewählt
			kilometer.remove(driveHome)
			auto.kapazitat -= sum(kilometer) * auto.spezVerbrauch #Erste Strecke fahren
			self.CalcFahrverbrauch(demand=sum(kilometer) * auto.spezVerbrauch,hour= hour, demandType= "Fahren")
			space = auto.maxLadung - auto.kapazitat
			auto.kapazitat = auto.maxLadung #Auto vollladen
			DS.ZV.gridCharging += space
			DS.ZV.emobilitätNetzGeladen += space
			DS.zeitVar.LadeLeistungExterneStationen[hour] += space / auto.effizienz
			auto.kapazitat -= driveHome * auto.spezVerbrauch #Letzte Strecke fahren
			self.CalcFahrverbrauch(demand=driveHome * auto.spezVerbrauch,hour= hour, demandType= "Fahren")
		else:
			auto.kapazitat -= sum(kilometer) * auto.spezVerbrauch
			self.CalcFahrverbrauch(demand=sum(kilometer) * auto.spezVerbrauch,hour= hour, demandType= "Fahren")



		if auto.kapazitat < 0:
			raise ValueError("Auto hat negative Ladung")

	def ChargeCars(self, cars:list, last:float, bTrack=False):
		"""Diese Funktion kümmert sich um das Laden der Autos. Es wird dabei nicht mit Netzstrom geladen
		cars: list
			Liste an Auto Objekten, welche geladen werden sollen
		last: float
			Residuallast die in die Autos geladen werden soll
		bTrack: bool
			bool der kontrolliert ob die maximale Ladung getrackt werden soll (das soll nur bei den eigenen Autos passieren)"""
		cars.sort(key=lambda x: x.kapazitat, reverse=True)
		leistung = last #Leistungs beschreibt die Energie, die geladen werden konnte
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
		leistung -= last
		return last, leistung

	def DischargeCars(self, last:float):
		"""Diese Funktion kümmert sich um das Entladen der Autos um die Gebäudelast abzudecken
		last: float
			Residuallast, welche abgedeckt werden soll
		"""
		cars = self.GetChargingCars() #Alle Autos die angesteckt sind und die mindestens die Mindestladung haben
		carstoDischarge = []
		for car in cars:
			if car.kapazitat > car.minLadung:
				carstoDischarge.append(car)
				car.diff = car.kapazitat - car.minLadung #Potenzielle entladbare Energie berechnen

		leistung = last #Leistungs beschreibt die Energie, die entladen werden konnte
		carstoDischarge.sort(key=lambda x: x.diff, reverse= True) #Autos werden nach der größten entladbaren Kapazität sortiert
		if carstoDischarge:
			for car in carstoDischarge:
				if last == 0: #Wenn die Last abgedeckt werden konnte, konnen wir früher abbrechen
					break
				qtoTake = min([car.leistung_MAX, last, car.diff]) #Die niedrigste Zahl davon kann entladen werden
				qtoTake -= car.Entladen(qtoTake)
				last -= qtoTake
				#if car.kapazitat < car.minLadung:
				#	raise ValueError("Auto zu niedrig entladen")

		leistung -= last
		return last, leistung

	def CheckMinKap(self, cars, hour, bTrack= False):
		"""Kontrolliert alle Autos, welche an der Ladestation laden.
		Falls Autos unter der Mindestladegrenze sind, werden diese aus dem Netz geladen"""
		
		for car in cars:
			if car.kapazitat < car.minLadung:
				space = (car.minLadung - car.kapazitat)
				toLoad = min([space, car.leistung_MAX, car.alreadyLoaded])
				car.Laden(toLoad/ car.effizienz)

				#if car.kapazitat > car.minLadung:
				#	raise ValueError("Kapazität ist zu Hoch")
				if bTrack:
					DS.ZV.emobilitätNetzGeladen += toLoad
					DS.ZV.gridCharging += toLoad
					DS.zeitVar.gridChargingHourly[hour] += toLoad  / car.effizienz


	def ResetAlreadyLoaded(self):
		"""Hilfsfunktion die eine Laufvariable zurücksetzt"""
		cars = self.GetChargingCars()
		for car in cars:
			car.alreadyLoaded = car.leistung_MAX

	def CalcUngenutzterSpeicherplatz(self, hour):
		"""Berechnet den Anteil der nicht verfügbaren Ladung für die bi-direktionalität
		Dabei wird der Anteil für alle Autos berechnet, die laden und mindestens die Mindestladung haben
		hour: int
			Stunde des Jahres"""
		cars = [car for car in self.GetChargingCars() if car.kapazitat > car.minLadung]

		if cars:
			maxLadung = sum([car.maxLadung for car in cars])
			minLadung = sum([car.minLadung for car in cars])
			aktLadung = sum([car.kapazitat for car in cars])
		
			genutzt = aktLadung - minLadung
			ungenutzt = maxLadung - aktLadung
			percent = ungenutzt / (ungenutzt+genutzt) * 100
			DS.zeitVar.ungenutzteLadung[hour] = percent
		else:
			DS.zeitVar.ungenutzteLadung[hour] = 100