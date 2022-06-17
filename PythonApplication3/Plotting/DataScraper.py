# -*- coding: cp1252 -*-
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import pandas as pd

class Scraper():
    def __init__(self):
     
        #Generelle Daten
        self.generell = {
            "personenKilometer Elektrisch durch. [km]" : 0, #Zählt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zurücklegt (km)
            "personenKilometer Elektrisch [km]" : 0, #Zählt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zurücklegt (km)
            "personenKilometer Fossil [km]" : 0, #Zählt wie viele Kilometer eine Person im Jahr mit dem Auto fossil zurücklegt (km)
            "stromverbrauch Wohnen [kWh]" : 0, #Verbrauch der Wohngebäude (kWh)
            "stromverbrauch Gewerbe [kWh]" : 0, #Verbrauch des Gewerbes (kWh)
            "stromverbrauch Schule [kWh]" : 0, #Verbrauch der Bildungsgebäude (kWh)
            "stromverbrauch WP [kWh]" : 0, #Verbrauch der Wärmepumpen (kWh)
            "stromverbrauch E-Mobilität [kWh]" : 0, #Verbrauch der E-Mobilität (kWh)
            "pvProduktion [kWh]" : 0, #Wie viel die PV-Anlage insgesamt produziert hat (kWh)
            "pvProduktionGfa [kWh]" : 0 #Wie viel PV Produktion pro m² gfa (kWh/m²gfa a)
            }
    
        #Indikatoren können auch Daten von anderen Gruppen enthalten
        #Indikatoren stellen die "Gesundheit" einer Variante dar
        self.indikatoren  = {
            #"Fahrversuche [Anzahl]" : 0, 
            "fehlgeschlagene Fahrversuche [%]" : 0, 
            "ungenutzte Ladung der E-Mobilität [%]" : 0,
            "erhöhung Eigenverbrauch [%]" : 0,
            "LadeEntlade_Zyklen ohne EMobilität pro Auto [Anzahl]" : 0,
            "LadeEntlade_Zyklen mit EMobilität pro Auto [Anzahl]" : 0,
            "Ladevorgänge [Anzahl]" : 0,
            "Entladevorgänge [Anzahl]" : 0,        
            }

        #Verbrauch der E-Mobilität zum Fahren
        self.eMobilitätFahren = {
            "Gesamt [kWh]" : 0,
            "Lokal [kWh]" : 0,
            "Netz [kWh]" : 0
            }

        #Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
        self.eMobilitätGebäude = {
            "Lade/Entladeverluste [kWh]" : 0,
            "GebäudezuEMobilität [kWh]" : 0, #Ohne Verluste
            "EMobilitätzuGebäude [kWh]" : 0  #Ohne Verluste                 
            }

        #PV-Daten vor E-Mobilität
        self.pvVorEMobilität = {
            "Eigenverbrauch [kWh]" : 0,
            "Einspeisung [kWh]" : 0,
            "Netzbezug [kWh]" : 0,
            }
        #PV-Daten nach E-Mobilität        
        self.pvNachEMobilität = {
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

        self.verbrauchFahrenEmobilität = 0

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