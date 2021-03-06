# -*- coding: cp1252 -*-
import Plotting.DataScraper as DS

from Ladecontroller_Helper import set_unit

class Person():

	def __init__(self):
		self.status = True #Status der Person True = Anwesend, False = Unterwegs
		self.anzAutoWege = 0 #Anzahl der Wege die mit dem Auto zur?ckgelegt werden
		self.km = [] #Laufvariable die die km f?r den derzeitigen Weg angeben
		self.wegMitAuto = 0 #Weg der insgesamt mit dem Auto zur?ckgelegt wurde
		self.carID = None #ID des zugewiesenen Autos
		self.minTimeAway = 0 #gibt an wie lange ein Auto mindestens weg sein muss

class Auto():

	def __init__(self,AutoDaten : dict, minLadung : float, counter = 0):
		self.leistung_MAX = AutoDaten["Lade/Entladeleistung"] #kW Maximale Lade-/Entladeleistung der Station
		self.effizienz = AutoDaten["Effizienz"] / 100 #Effizienz des Lade und Entladevorganges in Prozent (von 0-1)
		self.maxLadung = AutoDaten["maxLadung"] #Ladekapazitat des Autos in kWh
		self.minLadung = minLadung * self.maxLadung #minimale Ladung die eingehalten werden muss in kWh
		self.minLadungAbs = minLadung #minimale Ladung die eingehalten werden muss in Anteilen (von 0-1)
		self.kapazitat = self.maxLadung * self.minLadungAbs #Laufvariable in kWh
		self.bCharging = True #Wenn True dann ist das Auto an der Ladestation angeschlossen (True/False)
		self.bAvailable = True #Wenn True dann darf das Auto entnommen werden (True/False)
		self.verlust = 0 #Verlust von Lade/Entladevorgangen in kWh
		self.ID = counter #Unique ID die jedem Auto gegeben wird
		self.spezVerbrauch = AutoDaten["Verbrauch"] #kWh/km https://ev-database.de/cheatsheet/energy-consumption-electric-car
		self.alreadyLoaded = self.leistung_MAX	#Laufvariable die angibt wie viel nach der PV noch geladen werden darf

		DS.ZV.emobilit?tNetzGeladen += self.kapazitat

	@set_unit("kWh")
	def Laden(self, qtoLoad, hour):
		"""Ladet das Auto mit einer gegebenen Ladung
		qtoLoad: float,  
			Ladung mit dem das Auto geladen wird in kWh
		Return:
		qtoLoad: float,
			gibt den Input zuruck. Falls alles geladen werden konnte, ist der return 0"""
		if qtoLoad > self.leistung_MAX:
			#Wenn ja wird gekappt
			self.verlust = self.leistung_MAX * (1-self.effizienz)
			self.leistung = self.leistung_MAX * self.effizienz            
		else:
			#Wenn nein, g2g
			self.verlust = qtoLoad * (1-self.effizienz)
			self.leistung = qtoLoad * self.effizienz 
            
		#Kontrolle ob die Batterie uber die Maximale Kapazitat geladen werden wurde
		if self.kapazitat + self.leistung > self.maxLadung:
			self.verlust = (self.maxLadung - self.kapazitat) * (1-self.effizienz)
			self.leistung = (self.maxLadung - self.kapazitat) * self.effizienz
            
		#Ausfuhren des Ladevorgangs
		self.kapazitat += self.leistung
		qtoLoad -= (self.leistung + self.verlust)
        
		self.alreadyLoaded -= (self.leistung + self.verlust)
		return qtoLoad

	@set_unit("kWh")
	def Entladen(self, qtoTake, hour):
		"""Entladet das Auto mit einer gegebenen Ladung
		qtoTake: float,  
			Ladung mit dem das Auto entladen wird in kWh
		Return:
		qtoTake: float,
			gibt den Input zuruck. Falls alles entladen werden konnte, ist der return 0"""

		if qtoTake > self.leistung_MAX:
			#Wenn ja wird gekappt
			self.verlust = self.leistung_MAX * (1-self.effizienz)
			self.leistung = self.leistung_MAX * self.effizienz 
		else:
			#Wenn nein, g2g
			self.verlust = qtoTake * (1-self.effizienz) 
			self.leistung = qtoTake 

		#Kontrolle der Leistung
		if self.leistung + self.verlust > self.kapazitat:
			#Wenn nicht genugend Kapazitat vorhanden ist wird die Leistung gekappt
			self.verlust = self.kapazitat * (1-self.effizienz)
			self.leistung = self.kapazitat - self.verlust

		if self.kapazitat - (self.leistung + self.verlust) < self.minLadung:
			#Wenn die mindestladung unterschritten wird die Leistung gekappt
			self.verlust = (self.kapazitat - self.minLadung) * (1-self.effizienz)
			self.leistung = (self.kapazitat - self.minLadung) - self.verlust

		#Ausfuhren des Entladevorgangs
		self.kapazitat -= self.leistung + self.verlust
		qtoTake -= self.leistung 
		return qtoTake


	#def Speicherstand(self):
	#	"""Gibt den aktuellen Speicherstand in Anteilen (0-1) zuruck"""
	#	return abs(self.kapazitat) / self.maxLadung





