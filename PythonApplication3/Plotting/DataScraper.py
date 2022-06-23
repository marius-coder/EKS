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
            "fehlgeschlagene Fahrversuche [%]" : 0, #Anteil an Fahrversuchen der fehlgeschlagen ist
            "ungenutzte Ladung der E-Mobilit�t [%]" : 0, #Anteil der Ladung der E-Autos, welcher nicht benutzt worden ist (f�rs Laden)
            "erh�hung Eigenverbrauch [%]" : 0, #Anteil der angibt, wie sehr der Eigenverbrauch im Verlgiech ohne Ladecontroller erh�ht werden konnte
            "LadeEntlade_Zyklen ohne EMobilit�t pro Auto [Anzahl]" : 0,
            "LadeEntlade_Zyklen mit EMobilit�t pro Auto [Anzahl]" : 0,
            "Ladevorg�nge [Anzahl]" : 0, #Anzahl an insgesamt vorkommenden Ladevorg�ngen
            "Entladevorg�nge [Anzahl]" : 0, #Anzahl an insgesamt vorkommenden Entladevorg�ngen
            }

        #Verbrauch der E-Mobilit�t zum Fahren
        self.eMobilit�tFahren = {
            "Gesamt [kWh]" : 0, #Wie viel Energie wurde insgesamt durch das Fahren verbraucht
            "Lokal [kWh]" : 0, #Wie viel von der gefahrenen Energie wurde lokal erzeugt
            "Netz [kWh]" : 0, #Wie viel von der gefahrenen Energie wurde vom Netz bereitgestellt
            "externe Ladung [kWh]" : 0 #Energie die durch externe Ladestationen zugef�hgrt worden ist
            }

        #Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
        self.eMobilit�tGeb�ude = {
            "Lade/Entladeverluste [kWh]" : 0, #Lade
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

        #Daten der Au�enstehenden     
        self.au�enstehende = {
            "Ladung [kWH]" : 0,
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

class Zeitvariablen:

    def __init__(self):   

        self.StateofDrivingPersons = []
        self.StateofCars = []
        self.LadeLeistung = []
        self.LadeLeistungAu�enstehende = [0]*8760
        self.EntladeLeistung = []
        self.LadeLeistungExterneStationen = [0]*8760 #Geladene Energie von Externen Ladestationen

    def Export(self, szen):
        df = pd.DataFrame()
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attr in attributes:    
            data = getattr(self, attr)
            if type(data[0]) != list:
                df[f"{attr}"] = getattr(self, attr)
        df.to_csv(f"./Ergebnis/ZeitVar/Ergebnis_ZeitVar_Szenario"+szen+".csv", sep= ";", decimal= ",", encoding= "cp1252")

zeitVar = Zeitvariablen()