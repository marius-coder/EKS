# -*- coding: cp1252 -*-
import dataclasses as dataclass
import seaborn as sns
import matplotlib.pyplot as plt
import bokeh
import pandas as pd

@dataclass
class DataScraper():
    #Generelle Daten
    personenKilometer : float #Zählt wie viele Kilometer eine Person im Jahr mit dem Auto zurücklegt (km)
    stromverbrauchGebäude : float #Verbrauch des Gebäudes (kWh)
    pvProduktion : float #Wie viel die PV-Anlage insgesamt produziert hat (kWh)
    pvProduktionGfa : float #Wie viel PV Produktion pro m² gfa (kWh/m²gfa a)
    
    #Indikatoren können auch Daten von anderen Gruppen enthalten
    #Indikatoren stellen die "Gesundheit" einer Variante dar
    indikatoren = {
        #"Fahrversuche [Anzahl]" : 0, 
        "fehlgeschlagene Fahrversuche [%]" : 0, 
        "ungenutzte Ladung der E-Mobilität [%]" : 0,
        "erhöhung Eigenverbrauch [%]" : 0
        }

    #Verbrauch der E-Mobilität zum Fahren
    eMobilitätFahren = {
        "Gesamt [kWH]" : 0,
        "Lokal [kWH]" : 0,
        "Netz [kWH]" : 0
        }

    #Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
    eMobilitätGebäude = {
        "Lade/Entladeverluste [kWh]" : 0,
        "GebäudezuEMobilität [kWH]" : 0, #Ohne Verluste
        "EMobilitätzuGebäude [kWH]" : 0  #Ohne Verluste                 
        }

    #PV-Daten vor E-Mobilität
    pvVorEMobilität = {
        "Eigenverbrauch [kWh]" : 0,
        "Einspeisung [kWh]" : 0,
        "Netzbezug [kWh]" : 0,
        }
    #PV-Daten nach E-Mobilität        
    pvNachEMobilität = {
        "Eigenverbrauch [kWh]" : 0,
        "Einspeisung [kWh]" : 0,
        "Netzbezug [kWh]" : 0,
        }

    #Daten zu den einzelnen Gebäuden
    gebäudeDaten = {
        "Heizwärmebedarf [kWh/m²gfa]" : 0,
        "Kühlenergiebedarf [kWh/m²gfa]" : 0,
        "Warmwasserbedarf [kWh/m²gfa]" : 0,
        "Strombedarf Nutzer [kWh/m²gfa]" : 0,
        "Strombedarf Konditionierung [kWh/m²gfa]" : 0,
        "Primärenergiebedarf [kWh/m²gfa]" : 0,
        "CO2-Emissionen [tCO2]" : 0,
        }
    #Daten zu den einzelnen Gebäudeklassen (Wohnen, Gewerbe, Schule)
    gebäudeklassenDaten = {
        "Heizwärmebedarf [kWh/m²gfa]" : 0,
        "Kühlenergiebedarf [kWh/m²gfa]" : 0,
        "Warmwasserbedarf [kWh/m²gfa]" : 0,
        "Strombedarf Nutzer [kWh/m²gfa]" : 0,
        "Strombedarf Konditionierung [kWh/m²gfa]" : 0,
        "Primärenergiebedarf [kWh/m²gfa]" : 0,
        "CO2-Emissionen [tCO2]" : 0,
        }


    def __init__(self) -> None:
        self.Init_eMobility()

     
    def InitGeneral(self):

        
        

    def Init_eMobility(self):
        self.li_state = []			#Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)
        self.li_stateCars = []		#Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)
        self.useableCapacity = []	#Liste in der die verwendbare Kapazitat gespeichert wird zum plotten
        self.demandBuilding = []	#Liste in der der Bedarf des Gebäudes gespeichert wird
        self.demandDriving = []		#Liste in der der Bedarf der Autos zum Fahren gespeichert wird
        self.demandcovered = []		#Liste in der der Bedarf der durch die E-Autos gedeckt wird gespeichert wird
        self.PV = []		        #Liste in der die von auserhalb produzierte Leistung gespeichert wird
        self.generationloaded = []  #Liste die speichert, wie viel Energie in den Autos gespeichert wurde
        self.resLast = []           #Liste in der die Residuallast gespeichert wird
        self.demandDriven = 0       #Variable in der die zum Fahren verbrauchte Energie hochsummiert wird
        self.gridCharging = 0       #Variable in der die zum Fahren aus dem Netz bezogene Energie hochsummiert wird

        self.resLastDifferenceAfterDischarge = [0] * 8760
        self.resLastDifference = [0] * 8760
        self.resLastAfterDischarging = [0] * 8760
        self.resLastAfterCharging = [0] * 8760
        self.SOC = [] #Liste in der der SOC aller anwesenden Autos gespeichert wird


    def ExtractData(self, car):
        self.EGV = self.CalcEigenverbrauchmitAutoeinspeisung()
        self.plot2 = self.CalcFahrverbrauch(car)
    


Scraper = DataScraper()

