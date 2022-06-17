# -*- coding: cp1252 -*-
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import pandas as pd

class Scraper():
    def __init__(self):
     
        #Generelle Daten
        self.generell = {
            "personenKilometer Elektrisch durch. [km]" : 0, #Z�hlt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zur�cklegt (km)
            "personenKilometer Elektrisch [km]" : 0, #Z�hlt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zur�cklegt (km)
            "personenKilometer Fossil [km]" : 0, #Z�hlt wie viele Kilometer eine Person im Jahr mit dem Auto fossil zur�cklegt (km)
            "stromverbrauch Wohnen [kWh]" : 0, #Verbrauch der Wohngeb�ude (kWh)
            "stromverbrauch Gewerbe [kWh]" : 0, #Verbrauch des Gewerbes (kWh)
            "stromverbrauch Schule [kWh]" : 0, #Verbrauch der Bildungsgeb�ude (kWh)
            "stromverbrauch WP [kWh]" : 0, #Verbrauch der W�rmepumpen (kWh)
            "stromverbrauch E-Mobilit�t [kWh]" : 0, #Verbrauch der E-Mobilit�t (kWh)
            "pvProduktion [kWh]" : 0, #Wie viel die PV-Anlage insgesamt produziert hat (kWh)
            "pvProduktionGfa [kWh]" : 0 #Wie viel PV Produktion pro m� gfa (kWh/m�gfa a)
            }
    
        #Indikatoren k�nnen auch Daten von anderen Gruppen enthalten
        #Indikatoren stellen die "Gesundheit" einer Variante dar
        self.indikatoren  = {
            #"Fahrversuche [Anzahl]" : 0, 
            "fehlgeschlagene Fahrversuche [%]" : 0, 
            "ungenutzte Ladung der E-Mobilit�t [%]" : 0,
            "erh�hung Eigenverbrauch [%]" : 0,
            "LadeEntlade_Zyklen ohne EMobilit�t pro Auto [Anzahl]" : 0,
            "LadeEntlade_Zyklen mit EMobilit�t pro Auto [Anzahl]" : 0,
            "Ladevorg�nge [Anzahl]" : 0,
            "Entladevorg�nge [Anzahl]" : 0,        
            }

        #Verbrauch der E-Mobilit�t zum Fahren
        self.eMobilit�tFahren = {
            "Gesamt [kWh]" : 0,
            "Lokal [kWh]" : 0,
            "Netz [kWh]" : 0
            }

        #Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
        self.eMobilit�tGeb�ude = {
            "Lade/Entladeverluste [kWh]" : 0,
            "Geb�udezuEMobilit�t [kWh]" : 0, #Ohne Verluste
            "EMobilit�tzuGeb�ude [kWh]" : 0  #Ohne Verluste                 
            }

        #PV-Daten vor E-Mobilit�t
        self.pvVorEMobilit�t = {
            "Eigenverbrauch [kWh]" : 0,
            "Einspeisung [kWh]" : 0,
            "Netzbezug [kWh]" : 0,
            }
        #PV-Daten nach E-Mobilit�t        
        self.pvNachEMobilit�t = {
            "Eigenverbrauch [kWh]" : 0,
            "Einspeisung [kWh]" : 0,
            "Netzbezug [kWh]" : 0,
            }

    def Export(self, szen):
        df = pd.DataFrame()
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attr in attributes:
            for key, value in getattr(self,attr).items():
                df[f"{attr}_{key}"] = [value]
        df.to_csv(f"./Ergebnis/Ergebnis_Szenario"+szen+".csv", sep= ";", decimal= ",", encoding= "cp1252")
        

scraper = Scraper()

class Zwischenvariablen:

    def __init__(self):    

        self.verbrauchFahrenEmobilit�t = 0

        self.fahrversuche = 0
        self.fehlgeschlageneFahrversuche = 0

        self.maxLadung = 0
        self.aktuelleLadung = 0

        self.eMobilityCharge = [0]*8760
        self.eMobilityDischarge = [0]*8760
        self.counterCharging = 0
        self.counterDischarging = 0

        self.resLastBeforeEMobility = [0]*8760
        self.resLastAfterEMobility = [0]*8760
        self.resLastAfterDischarging = [0]*8760 

        self.gridCharging = 0

ZV = Zwischenvariablen()

class Zwischenvariablen:

    def __init__(self):   

        self.StateofDrivingPersons = [[]*8760]
        self.StateofCars = [[]*8760]
        self.LadeLeistung = [0]*8760