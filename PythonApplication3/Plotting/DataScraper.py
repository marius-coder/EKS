# -*- coding: cp1252 -*-
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import pandas as pd

class Scraper():
    def __init__(self):

        #Generelle Daten
        self.generell = {
            "personenKilometer Elektrisch durch. [km]" : 0, #Zählt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zurücklegt (km)
            "personenKilometer Elektrisch [km]" : 0, #Zählt wie viele Kilometer alle Personen im Jahr mit dem Auto elektrisch zurücklegt (km)
            "personenKilometer Fossil [km]" : 0, #Zählt wie viele Kilometer alle Personen im Jahr mit dem Auto fossil zurücklegt (km)
            "stromverbrauch Wohnen [kWh/m²]" : 0, #Verbrauch der Wohngebäude (kWh)
            "stromverbrauch Gewerbe [kWh/m²]" : 0, #Verbrauch des Gewerbes (kWh)
            "stromverbrauch Schule [kWh/m²]" : 0, #Verbrauch der Bildungsgebäude (kWh)
            "stromverbrauch WP [kWh/m²]" : 0, #Verbrauch der Wärmepumpen (kWh)
            "stromverbrauch E-Mobilität [kWh/Auto]" : 0, #Verbrauch der E-Mobilität zum Fahren (kWh)
            "pvProduktion [kWh/m²]" : 0, #Wie viel die PV-Anlage insgesamt produziert hat (kWh)
            "pvProduktionGfa [kWh/m²]" : 0 #Wie viel PV Produktion pro m² gfa (kWh/m²gfa a)
            }
    
        #Indikatoren können auch Daten von anderen Gruppen enthalten
        #Indikatoren stellen die "Gesundheit" einer Variante dar
        self.indikatoren  = {
            "fehlgeschlagene Fahrversuche [%]" : 0, #Anteil an Fahrversuchen der fehlgeschlagen ist
            "ungenutzte Ladung der E-Mobilität [%]" : 0, #Anteil der Ladung der E-Autos, welcher nicht benutzt worden ist (fürs Laden)
            "erhöhung Eigenverbrauch E-Mobilität [%]" : 0, #Anteil der angibt, wie sehr der Eigenverbrauch im Vergleich ohne Ladecontroller erhöht werden konnte
            "erhöhung Eigenverbrauch Zureisende [%]" : 0, #Anteil der angibt, wie sehr der Eigenverbrauch durch die Zureisenden erhöht wird
            "LadeEntlade_Zyklen pro Auto [Anzahl]" : 0,
            }

        #Verbrauch der E-Mobilität zum Fahren
        self.eMobilitätFahren = {
            "Gesamt [kWh/Auto]" : 0, #Wie viel Energie wurde insgesamt durch das Fahren verbraucht
            "Lokal [kWh/Auto]" : 0, #Wie viel von der gefahrenen Energie wurde lokal erzeugt
            "Netz [kWh/Auto]" : 0, #Wie viel von der gefahrenen Energie wurde vom Netz bereitgestellt
            "externe Ladung [kWh/Auto]" : 0 #Energie die durch externe Ladestationen zugefühgrt worden ist
            }

        #Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
        self.eMobilitätGebäude = {
            "Lade/Entladeverluste [kWh/Auto]" : 0, #Lade
            "GebäudezuEMobilität [kWh/Auto]" : 0, #Ohne Verluste / Verluste rausgerechnet
            "EMobilitätzuGebäude [kWh/Auto]" : 0  #Ohne Verluste / Verluste rausgerechnet
            }

        #PV-Daten vor E-Mobilität
        self.pvVorEMobilität = {
            "Eigenverbrauch [kWh/m²]" : 0,
            "Einspeisung [kWh/m²]" : 0,
            "Netzbezug [kWh/m²]" : 0,
            }
        #PV-Daten nach E-Mobilität        
        self.pvNachEMobilität = {
            "Eigenverbrauch [kWh/m²]" : 0,
            "Einspeisung [kWh/m²]" : 0,
            "Netzbezug [kWh/m²]" : 0,
            }

        self.pvNachZureisenden = {
            "Eigenverbrauch [kWh/m²]" : 0,
            "Einspeisung [kWh/m²]" : 0,
            "Netzbezug [kWh/m²]" : 0,
            }

        #Daten der Außenstehenden     
        self.zureisenden = {
            "Ladung [kWh/m²]" : 0,
        }

    def Export(self, szen):
        df = pd.DataFrame()
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attr in attributes:
            for key, value in getattr(self,attr).items():
                df[f"{attr}_{key}"] = [value]
        df.to_csv(f"./Ergebnis/Indikatoren/Ergebnis_Szenario"+szen+".csv", sep= ";", decimal= ",", encoding= "cp1252")
        

scraper = Scraper()

class Zwischenvariablen:

    def __init__(self):    

        self.verbrauchFahrenEmobilität = 0

        self.fahrversuche = 0
        self.fehlgeschlageneFahrversuche = 0

        self.maxLadung = 0
        self.aktuelleLadung = 0 #maximal Vorgekommene Ladung

        self.gridCharging = 0

        self.emobilitätErneuerbarGeladen = 0
        self.emobilitätNetzGeladen = 0




ZV = Zwischenvariablen()

class Zeitvariablen:

    def __init__(self):   

        self.StateofDrivingPersons = []
        self.StateofCars = []
        self.eMobilityCharge = [0]*8760
        self.LadeLeistungAußenstehende = [0]*8760
        self.eMobilityDischarge = [0]*8760
        self.LadeLeistungExterneStationen = [0]*8760 #Geladene Energie von Externen Ladestationen

        self.resLastBeforeEMobility = [0]*8760
        self.resLastAfterEMobility = [0]*8760
        self.resLastAfterZureisende = [0]*8760

        self.gridChargingHourly = [0]*8760
        self.pvChargingHourly = [0]*8760
        self.buildingDemandHourly = [0]*8760
        self.carDemandHourly = [0]*8760
        
        self.fahrverbrauchLokal = [0]*8760
        self.fahrverbrauchNetz = [0]*8760
        
        self.entladungLokal = [0]*8760
        self.entladungNetz = [0]*8760

        self.ungenutzteLadung = [0]*8760 #Prozent der ungenutzten Ladung

    def Export(self, szen):
        df = pd.DataFrame()
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attr in attributes:    
            data = getattr(self, attr)
            if type(data[0]) != list:
                df[f"{attr}"] = getattr(self, attr)
        df.to_csv(f"./Ergebnis/ZeitVar/Ergebnis_ZeitVar_Szenario"+szen+".csv", sep= ";", decimal= ",", encoding= "cp1252")

zeitVar = Zeitvariablen()