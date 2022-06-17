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
    indikatoren = {
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
    eMobilitätFahren = {
        "Gesamt [kWh]" : 0,
        "Lokal [kWh]" : 0,
        "Netz [kWh]" : 0
        }

    #Daten zu den Energieflüssen zwischen E-Mobilität und Gebäude
    eMobilitätGebäude = {
        "Lade/Entladeverluste [kWh]" : 0,
        "GebäudezuEMobilität [kWh]" : 0, #Ohne Verluste
        "EMobilitätzuGebäude [kWh]" : 0  #Ohne Verluste                 
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
scraper = Scraper()

@dataclass
class Zwischenvariablen:
    verbrauchFahrenEmobilität : float = 0

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