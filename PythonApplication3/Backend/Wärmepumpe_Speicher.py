
import pandas as pd
import os
import csv
import numpy as np


class Speicher():
    """Der Wärmespeicher ist simpel abgebildet und unterstützt simple Funktionen wie laden/entladen sowie das Abfragen des Ladestandes
    TODO: Keine weiteren Verbesserungen geplant"""


    def __init__(self, MAX_Speicherstand):

        self.MAX_Speicherstand  = MAX_Speicherstand #Maximaler Speicherstand in kWh
        self.speicherstand = self.MAX_Speicherstand / 2 #Momentaner Speicherstand in kWh

    def Speicherstand(self):
        """Gibt den aktuellen Speicherstand in Anteilen zurück"""
        return self.speicherstand / self.MAX_Speicherstand

    def SpeicherLaden(self, qtoLoad):
        """Nimmt als Argument wie viel Energie in den Speicher geladen werden soll
        Konstrolliert dabei ob der Speicher überladen wird"""

        self.speicherstand += qtoLoad
        rest = 0

        #Falls der Speicher überfüllt werden würde, wird dieser gekappt und der Rest returned
        if self.speicherstand > self.MAX_Speicherstand:
            rest = self.speicherstand - self.MAX_Speicherstand
            self.speicherstand = self.MAX_Speicherstand
        return rest

    def SpeicherEntladen(self, qtoTake, MIN_Speicherstand):
        """Nimmt als Argument wie viel Energie dem Speicher entnommen werden soll
        Konstrolliert dabei ob der Speicher unterladen wird"""
            
        self.speicherstand -= qtoTake
        rest = 0

        if self.speicherstand < MIN_Speicherstand:
            rest = MIN_Speicherstand - self.speicherstand
            self.speicherstand = MIN_Speicherstand
        return rest


class Wärmepumpe():
    """Wärmepumpenklasse mit simplen COP für Heizen und Warmwasser.
    TODO: PV geführtes Laden des Speichers. (Mit Prioritätensystem für E-Mobilität und Haushaltsstrom)
    TODO: Variabler COP nach Außentemperatur für Luftwärmepumpe
    """

    def __init__(self, speicher, COP_HZG, COP_WW, Pel):
        self.COP_HZG = 3  #COP im Heizbetrieb
        self.COP_WW = 2 #COP im Warmwasserbetrieb
        self.Pel = 3 #Elektrische Leistungsaufnahme in kW

        self.hystEin = 0.2 #Gibt an ab welchen Ladestand sich die Wärmepumpe einschalten soll
        self.hystAus = 0.8 #Gibt an ab welchen Ladestand sich die Wärmepumpe ausschalten soll

        self.type = "Luft" #Gibt des Typen der Wärmepumpe an. Optionen: Wasser/Luft
        self.bIsOn = False #Legt fest ob die Wärmepumpe gerade eingeschalten ist

        self.speicher = speicher  #Falls ein Speicher vorhanden ist wird dieser hier definiert


    def ProcessStep(self, mode):
        if mode == "WW":
            return self.COP_WW * self.Pel
        else:
            return self.COP_HZG * self.Pel

    def TurnOn(self):
        """Schaltet die Wärmepumpe ein"""
        self.bIsOn = True

    def TurnOff(self):
        self.bIsOn = False

    def CheckSpeicher(self, mode):
        """Simple Regelung für den Speicher
        mode: Modus in der die Wärmepume fährt || Optionen: HZG/WW"""

        if self.bIsOn == False: #Nur wenn die WP nicht läuft müssen wir kontrollieren ob der Speicher unter der Ladegrenze ist
            if self.speicher.Speicherstand() < self.hystEin:
                    self.TurnOn()
        if self.bIsOn == True:
            qHeat = self.ProcessStep(mode)
            rest = self.speicher.SpeicherLaden(qHeat)
            if rest != 0: #Falls der Speicher zu voll geladen wird, wird die geladene Energie reduziert
                qHeat -= rest

        if self.speicher.Speicherstand() > self.hystAus:
            self.TurnOff()

test_Speicher = Speicher(MAX_Speicherstand = 100, MIN_Speicherstand = 0)
test_WP = Wärmepumpe(speicher = test_Speicher)
for i in range(30):
    test_WP.speicher.SpeicherEntladen(5, test_WP.hystEin)
    test_WP.CheckSpeicher(mode = "HZG")
    print(f"Status WP: {test_WP.bIsOn}")
    print(f"Ladestand Speicher: {test_WP.speicher.speicherstand}")
    print("--------------------------")