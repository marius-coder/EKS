# -*- coding: cp1252 -*-


class Dataflows():


    def __init__(self) -> None:
        self.tInnen = []  #Liste die die Innentemperaturen der Geb�ude enth�lt
        self.qHL = []  #Liste mit den Energieflussen des Gebaudes
        self.qWW = []  #Liste mit dem Warmwasserverbrauch des Gebaudes
        self.stromBedarf = [] #Liste die den Strombedarf aller Nutzer enthalt (Wohnen+Gewerbe)
        
        self.interneGewinne = [0] * 8760 #Interne W�rmegewinne (Personen,Licht,Maschinen)
        self.solareGewinne = [0] * 8760 #Solare Gewinne
        self.ventilationVerluste = [0] * 8760 #Ventilationsw�rmeverluste
        self.infiltrationVerluste = [0] * 8760 #Infiltrationsw�rmeverluste
        self.transmissionVerluste = [0] * 8760 #Transmissionsw�rmeverluste
        
    def InitSzenWP(self):
        self.stromWP_HZG = [] #Liste mit dem verbrauchten Strom der Warmepumpe fur Heizen
        self.qWP_HZG = []     #Liste mit der erzeugten W�rme der Warmepumpe fur Heizen

        self.stromWP_WW = []  #Liste mit dem verbrauchten Strom der Warmepumpe fur Warmwasser
        self.qWP_WW = []      #Liste mit der erzeugten W�rme der Warmepumpe fur Warmwasser

    def InitSzenFW(self):
        self.stromWP_HZG = [] #Liste mit dem verbrauchten Strom der Warmepumpe fur Heizen
        self.qWP_HZG = []     #Liste mit der erzeugten W�rme der Warmepumpe fur Heizen

