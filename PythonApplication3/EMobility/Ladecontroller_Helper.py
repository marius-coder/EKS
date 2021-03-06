# -*- coding: cp1252 -*-
from itertools import count
from random import seed, choices, uniform
from collections import Counter
from numpy.random import Generator, PCG64
import numpy as np
import pandas as pd
import holidays

#from Auto_Person import Auto

rng = Generator(PCG64(10))
seed(10)

def CalcMobilePersonen(day, personen) -> int:
    """Diese Funktion berechnet die Anzahl mobiler Personen pro Tag.
    personen: int
        Anzahl der im Quartier lebenden Personen
    return: int
        Anzahl mobiler Personen"""
    if day == "Werktag":
        factor = 0.83
    elif day == "Samstag":
        factor = 0.77
    elif day == "Sonntag":
        factor = 0.66
    return int(personen * factor)
   
def GenerateWeightedItem(pop, weights):
	"""Gibt eine Zahl/String, mit einer custom Gewichtung zuruck
    pop: list
        Liste an Auswahlmoglichkeiten
    wheights: list
        Liste an gewichten nach denen gewahlt wird        
    return: int/float/string
        Gibt eine Zahl/String zuruck"""
	return choices(pop, weights)[0]

def CalcNumberofWays(day) -> int:
    """Gibt die Anzahl der moglichen Wege zuruck die eine Person am Tag zurucklegen kann
    day: string
        Typ des Tages"""
    population = [2,3,4,5]
    if day in ["Werktag","Samstag"]:
        weights = [20,45,25,10]
    elif day == "Sonntag":
        weights = [40,45,10,5]
    return GenerateWeightedItem(pop= population, weights= weights)

def GenerateWegZweck(day) -> int:
    """Generiert aufgrund des Tages einen Wegzweck
    day: string
        Typ des Tages"""
    population = ["Arbeitsplatz","Bring_Holweg","Freizeit","Dienstlich","Einkaufen","Besuch","Schule","Erledigung"]
    if day == "Werktag":
        weights = [27,7,15,5,17,8,8,13] 
    elif day == "Samstag":
        weights = [7,5,31,2,30,12,1,12]
    elif day == "Sonntag":
        weights = [5,5,47,2,3,26,1,11]        
    return GenerateWeightedItem(pop= population, weights= weights)

def GenerateTransportmittel(zweck) -> str:
    """Je nach Wegzweck ergibt sich eine Warscheinlichkeit ob das Auto als Transportmittel gewahlt wird
    zweck: string
        zweck fur den gewahlten Weg"""
    population = ["zuFus","Rad","AutolenkerIn","MitfahrerIn","Offentlich","Anderes"]
    if zweck == "Arbeitsplatz":
        weights = [8,7,60,5,20,0] 
    elif zweck == "Bring_Holweg":
        weights = [16,2,67,9,6,0] 
    elif zweck == "Freizeit":
        weights = [30,10,30,17,12,1] 
    elif zweck == "Dienstlich":
        weights = [6,3,70,8,11,2]  
    elif zweck == "Einkaufen":
        weights = [25,8,45,13,9,0] 
    elif zweck == "Besuch":
        weights = [19,7,45,18,11,0] 
    elif zweck == "Schule":
        weights = [21,6,9,16,48,0] 
    elif zweck == "Erledigung":
        weights = [17,6,47,15,14,1] 
    return GenerateWeightedItem(pop= population, weights= weights)

def GenerateKilometer() -> float:
    """Gibt zuruckgelegte km zuruck. Der Bereich der km wird zuerst mit einer Warscheinlichkeit festgelegt"""
    population = [[0,0.5],[0.5,1],[1,2.5],[2.5,5],[5,10],[10,20],[20,50],[50,70]]
    weights = [2,5,12,21,21,19,15,5] 
    bereich = GenerateWeightedItem(pop= population, weights= weights)
    return uniform(bereich[0],bereich[1])

def GenerateNormalNumber(mean:float ,std:float) -> float:
    """Generiert eine zuf?llige normalverteilte Zahl.
        Falls die generierte Zahl au?erhalb der dreifachen std liegt, wird nochmal generiert
        mean: int
            Mittelpunkt der Normalverteilung
        std: float
            Gew?nschte Abweichung der zur?lligen Zahl"""
    std = std/3
    val = rng.normal(loc= mean, scale= std, size= 1)

    if mean - val < 3*std:
        return float(val)
    else:
        GenerateNormalNumber(mean,std)
        return float(val)



def GenerateReiseProfil(profil : list, prozent : int) -> list:
    """ Generiert ein zuf?lliges Profil mit einer gegebenen Abweichung
    Im Anschluss wird das Profil auf 100% korrigiert
    profil: list
        profil welches randomized werden soll
    prozent: int
        Abweichung, welche auf jeden Punkt angewandt wird
    """
    if prozent != 0:
        ret = []
        for i in range(len(profil)):
            mean = profil[i]
            std = mean * prozent
            ret.append(GenerateNormalNumber(mean= mean, std= std))

        factor = 100/sum(ret)
        ret = [x*factor for x in ret]
        return ret
    else:
        return profil

uberlauf = 0 #Uberlauf gibt an, ob ein Autoweg auf 2 aufgestockt werden soll.
def CalcAutoWege(ways, day) -> int:
    """Berechnet die Anzahl der Autowege. 
    Autowege mit Anzahl eins werden korrigiert
    ways: int
            Anzahl der Wege
    day: string
        Typ des Tages"""
    global uberlauf 
    gesTransport = []
    for _ in range(ways):
        zweck = GenerateWegZweck(day)
        gesTransport.append(GenerateTransportmittel(zweck))

    ret = dict(Counter(gesTransport))
    if "AutolenkerIn" in ret:
        if ret["AutolenkerIn"] == 1:
            if uberlauf == 0:        
                #Anzahl Autowege auf 0 setzen
                uberlauf = 1
                return 0
            else:
                #Anzahl Autowege auf 2 setzen
                uberlauf = 0
                return 2                
        else:
            #Falls die Anzahl groser gleich 2 ist, kann returned werden
            return ret["AutolenkerIn"]
    else:
        return 0

def CalcEMobilityBuildingEnergyFlows(discharge:float, charge:float, externCharge:float, car):
    """
    Berechnet diverse Energiefl?sse zwischen dem Geb?ude und der Ladestation
    discharge: float
        Energie die aus den Autos entladen wurde (Verluste schon miteinberechnet)
    charge: float
        Energie mit der die Autos geladen worden sind (Keine Verluste einberechnet)
    externCharge: float
        Energie die durch externe Ladestationen zugef?hrt worden ist
    """
    verlustLaden = charge * (1-car.effizienz)  #Verlust durch laden der Autos
    vorFahren = charge - verlustLaden  #Energie die nach dem Laden den Autos zum Fahren zur Verf?gung steht

    nachFahren = discharge / car.effizienz #Energie die nach dem Fahren dem Geb?ude zur Verf?gung steht
    verlustEntladen = nachFahren * (1-car.effizienz) #Verlust durch Entladen der Autos
    Geb?udeVerbrauch = nachFahren - verlustEntladen #Energie die nach den Verlusten dem Geb?ude zugef?hrt wird
    verlustGesamt = verlustEntladen + verlustLaden #Insgesamte Verluste    
    Fahrverbrauch = vorFahren - (nachFahren - externCharge) #Energie die durch Fahren verbraucht wurde

    return Geb?udeVerbrauch, Fahrverbrauch, verlustGesamt


def CalcEigenverbrauch(pv:list, resLast:list): 
    """Berechnet den Eigenverbrauch
    pv: list
        Liste mit PV-Erzeugung
    resLast: list
        Liste mit der Residuallast"""
    pv = pv[0:len(resLast)]
    Einspeisung = abs(sum([x for x in resLast if x < 0]))

    Eigenverbrauchsanteil = 1 - Einspeisung/sum(pv)
    Eigenverbrauch = int(sum(pv) * Eigenverbrauchsanteil)
    ?berschuss = int(sum(pv) - sum(pv) * Eigenverbrauchsanteil)
    return Eigenverbrauch, ?berschuss

def DetermineMonth(hour):
	if 0 <= hour <= 744:
		return 1
	elif 744 < hour <= 1416:
		return 2
	elif 1416 < hour <= 2160:
		return 3
	elif 2160 < hour <= 2880:
		return 4
	elif 2880 < hour <= 3624:
		return 5
	elif 3624 < hour <= 4344:
		return 6
	elif 4344 < hour <= 5088:
		return 7
	elif 5088 < hour <= 5832:
		return 8
	elif 5832 < hour <= 6552:
		return 9
	elif 6552 < hour <= 7296:
		return 10
	elif 7296 < hour <= 8016:
		return 11
	elif 8016 < hour <= 8760:
		return 12


def DetermineHourofDay(hour):
	return (hour) % 24

time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)
Feiertage = holidays.country_holidays('Austria')


def DetermineDay(hour) -> str:
	"""Findet den Typ des Tages heraus. Achtet dabei auf Feiertage.
	hour: int
		Stunde des Jahres"""
	if time[hour] in Feiertage:
		#Feiertage werden als Sonntage gehandhabt
		return "Sonntag"
	if time[hour].weekday() == 5:
		return "Samstag"
	elif time[hour].weekday() == 6:
		return "Sonntag"
	else:
		return "Werktag"

def set_unit(unit):
    """Register a unit on a function"""
    def decorator_set_unit(func):
        func.unit = unit
        return func
    return decorator_set_unit