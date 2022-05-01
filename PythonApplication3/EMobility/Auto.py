
class Auto():

	def __init__(self, maxLadung, minLadung):
		self.leistung_MAX = 20 #kW Maximale Lade-/Entladeleistung der Station
		self.effizienz = 0.95 #Effizienz des Lade und Entladevorganges in Prozent (von 0-1)
		self.maxLadung = maxLadung #Ladekapazitat des Autos in kWh
		self.minLadung = minLadung #minimale Ladung die eingehalten werden muss in Anteilen (von 0-1)
		self.kapazitat = maxLadung #Laufvariable in kWh
		self.bCharging = True #Wenn True dann ist das Auto an der Ladestation angeschlossen (True/False)

	def Laden(self, qtoLoad):
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
        
		return qtoLoad

	def Entladen(self, qtoTake):

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

		if self.kapazitat - (self.leistung + self.verlust) < self.minLadung * self.maxLadung:
			#Wenn die mindestladung unterschritten wird die Leistung gekappt
			self.verlust = (self.kapazitat - self.minLadung * self.maxLadung) * (1-self.effizienz)
			self.leistung = (self.kapazitat - self.minLadung * self.maxLadung) - self.verlust

		#Ausfuhren des Entladevorgangs
		self.kapazitat -= self.leistung + self.verlust
		qtoTake -= self.leistung 

		return qtoTake

	def Speicherstand(self):
		"""Gibt den aktuellen Speicherstand in Anteilen zuruck"""
		return self.kapazitat / self.maxLadung