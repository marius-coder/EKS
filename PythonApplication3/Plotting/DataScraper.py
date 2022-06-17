# -*- coding: cp1252 -*-
from dataclasses import dataclass, field
import seaborn as sns
import matplotlib.pyplot as plt
import bokeh
import pandas as pd

@dataclass
class Scraper:
    #Generelle Daten
    generell = {
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
    indikatoren = {
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
    eMobilit�tFahren = {
        "Gesamt [kWh]" : 0,
        "Lokal [kWh]" : 0,
        "Netz [kWh]" : 0
        }

    #Daten zu den Energiefl�ssen zwischen E-Mobilit�t und Geb�ude
    eMobilit�tGeb�ude = {
        "Lade/Entladeverluste [kWh]" : 0,
        "Geb�udezuEMobilit�t [kWh]" : 0, #Ohne Verluste
        "EMobilit�tzuGeb�ude [kWh]" : 0  #Ohne Verluste                 
        }

    #PV-Daten vor E-Mobilit�t
    pvVorEMobilit�t = {
        "Eigenverbrauch [kWh]" : 0,
        "Einspeisung [kWh]" : 0,
        "Netzbezug [kWh]" : 0,
        }
    #PV-Daten nach E-Mobilit�t        
    pvNachEMobilit�t = {
        "Eigenverbrauch [kWh]" : 0,
        "Einspeisung [kWh]" : 0,
        "Netzbezug [kWh]" : 0,
        }
scraper = Scraper()

@dataclass
class Zwischenvariablen:
    verbrauchFahrenEmobilit�t : float = 0

    fahrversuche : int = 0
    fehlgeschlageneFahrversuche : int = 0

    maxLadung : float = 0
    aktuelleLadung : float = 0

    eMobilityCharge : list[list] = field(default_factory=lambda: [0]*8760)
    eMobilityDischarge : list[list] = field(default_factory=lambda: [0]*8760)
    counterCharging : int = 0
    counterDischarging : int = 0

    resLastBeforeEMobility : list[list] = field(default_factory=lambda: [0]*8760)
    resLastAfterEMobility : list[list] = field(default_factory=lambda: [0]*8760)

    gridCharging : float = 0

ZV = Zwischenvariablen()