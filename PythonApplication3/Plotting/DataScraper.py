# -*- coding: cp1252 -*-
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import pandas as pd

class Scraper():
    def __init__(self):

        #Generelle Daten
        self.generell = {
            "personenKilometer Elektrisch durch. [km]" : 0, #Z�hlt wie viele Kilometer eine Person im Jahr mit dem Auto elektrisch zur�cklegt (km)
            "personenKilometer Elektrisch [km]" : 0, #Z�hlt wie viele Kilometer alle Personen im Jahr mit dem Auto elektrisch zur�cklegt (km)
            "personenKilometer Fossil [km]" : 0, #Z�hlt wie viele Kilometer alle Personen im Jahr mit dem Auto fossil zur�cklegt (km)
            "stromverbrauch Wohnen [kWh/m�]" : 0, #Verbrauch der Wohngeb�ude (kWh)
            "stromverbrauch Gewerbe [kWh/m�]" : 0, #Verbrauch des Gewerbes (kWh)
            "stromverbrauch Schule [kWh/m�]" : 0, #Verbrauch der Bildungsgeb�ude (kWh)
            "stromverbrauch WP [kWh/m�]" : 0, #Verbrauch der W�rmepumpen (kWh)
            "stromverbrauch E-Mobilit�t [kWh/Auto]" : 0, #Verbrauch der E-Mobilit�t zum Fahren (kWh)
            "pvProduktion [kWh/m�]" : 0, #Wie viel die PV-Anlage insgesamt produziert hat (kWh)
            "pvProduktionGfa [kWh/m�]" : 0 #Wie viel PV Produktion pro m� gfa (kWh/m�gfa a)
            }
    
        #Indikatoren k�nnen auch Daten von anderen Gruppen enthalten
        #Indikatoren stellen die "Gesundheit" einer Variante dar
        self.indikatoren  = {
            "fehlgeschlagene Fahrversuche [%]" : 0, #Anteil an Fahrversuchen der fehlgeschlagen ist
            "ungenutzte Ladung der E-Mobilit�t [%]" : 0, #Anteil der Ladung der E-Autos, welcher nicht benutzt worden ist (f�rs Laden)
            "erh�hung Eigenverbrauch E-Mobilit�t [%]" : 0, #Anteil der angibt, wie sehr der Eigenverbrauch im Vergleich ohne Ladecontroller erh�ht werden konnte
            "erh�hung Eigenverbrauch Zureisende [%]" : 0, #Anteil der angibt, wie sehr der Eigenverbrauch durch die Zureisenden erh�ht wird
            "LadeEntlade_Zyklen pro Auto [Anzahl]" : 0,
            }

        #Verbrauch der E-Mobilit�t zum Fahren
        self.eMobilit�tFahren = {
            "Gesamt [kWh/Auto]" : 0, #Wie viel Energie wurde insgesamt durch das Fahren verbraucht
            "Lokal [kWh/Auto]" : 0, #Wie viel von der gefahrenen Energie wurde lokal erzeugt
            "Netz [kWh/Auto]" : 0, #Wie viel von der gefahrenen Energie wurde vom Netz bereitgestellt
            "externe Ladung [kWh/Auto]" : 0 #Energie die durch externe Ladestationen zugef�hgrt worden ist
            }

        #Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
        self.eMobilit�tGeb�ude = {
            "Lade/Entladeverluste [kWh/Auto]" : 0, #Lade
            "Geb�udezuEMobilit�t [kWh/Auto]" : 0, #Ohne Verluste / Verluste rausgerechnet
            "EMobilit�tzuGeb�ude [kWh/Auto]" : 0  #Ohne Verluste / Verluste rausgerechnet
            }

        #PV-Daten vor E-Mobilit�t
        self.pvVorEMobilit�t = {
            "Eigenverbrauch [kWh/m�]" : 0,
            "Einspeisung [kWh/m�]" : 0,
            "Netzbezug [kWh/m�]" : 0,
            }
        #PV-Daten nach E-Mobilit�t        
        self.pvNachEMobilit�t = {
            "Eigenverbrauch [kWh/m�]" : 0,
            "Einspeisung [kWh/m�]" : 0,
            "Netzbezug [kWh/m�]" : 0,
            }

        self.pvNachZureisenden = {
            "Eigenverbrauch [kWh/m�]" : 0,
            "Einspeisung [kWh/m�]" : 0,
            "Netzbezug [kWh/m�]" : 0,
            }

        #Daten der Au�enstehenden     
        self.zureisenden = {
            "Ladung [kWh/m�]" : 0,
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

        self.verbrauchFahrenEmobilit�t = 0

        self.fahrversuche = 0
        self.fehlgeschlageneFahrversuche = 0

        self.maxLadung = 0
        self.aktuelleLadung = 0 #maximal Vorgekommene Ladung

        self.gridCharging = 0

        self.emobilit�tErneuerbarGeladen = 0
        self.emobilit�tNetzGeladen = 0




ZV = Zwischenvariablen()

class Zeitvariablen:

    def __init__(self):   

        self.StateofDrivingPersons = []
        self.StateofCars = []
        self.eMobilityCharge = [0]*8760
        self.LadeLeistungAu�enstehende = [0]*8760
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