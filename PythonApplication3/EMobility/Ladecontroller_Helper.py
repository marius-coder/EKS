# -*- coding: <latin-1> -*-
from random import seed, choices
from miscellaneous import *
seed(10)
def CalcMobilePersonen(day, personen):
    if day == "Werktag":
        factor = 0.83
    elif day == "Samstag":
        factor = 0.77
    elif day == "Sonntag":
        factor = 0.66
    return personen * factor
   
def GenerateWeightedItem(pop, weights):
	"""Gibt eine Zahl/String, mit einer custom Gewichtung, zwischen 2-5 zuruck"""
	return choices(pop, weights)[0]

def CalcNumberofWays(day):
    """Gibt die Anzahl der moglichen Wege zuruck die eine Person am Tag zurucklegen kann"""
    population = [2,3,4,5]
    if day in ["Werktag","Samstag"]:
        weights = [20,45,25,10]
    elif day == "Sonntag":
        weights = [40,45,10,5]
    return GenerateWeightedItem(pop= population, weights= weights)

def GenerateWegZweck(day):
    """Generiert aufgrund des Tages einen Wegzweck"""
    population = ["Arbeitsplatz","Bring_Holweg","Freizeit","Dienstlich","Einkaufen","Besuch","Schule","Erledigung"]
    if day == "Werktag":
        weights = [27,7,15,5,17,8,8,13] 
    elif day == "Samstag":
        weights = [7,5,31,2,30,12,1,12]
    elif day == "Sonntag":
        weights = [5,5,47,2,3,26,1,11]        
    return GenerateWeightedItem(pop= population, weights= weights)

def GenerateIfDriving(zweck):
    """Je nach Wegzweck ergibt sich eine Warscheihnlichkeit ob das Auto als Transportmittel gew�hlt wird"""
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

def GenerateKilometer():
    """Gibt zuruckgelegte km zuruck. Der Bereich der km wird zuerst mit einer Warscheinlichkeit festgelegt"""
    population = [[0,0.5],[0.5,1],[1,2.5],[2.5,5],[5,10],[10,20],[20,50],[50,70]]
    weights = [2,5,12,21,21,19,15,5] 
    bereich = GenerateWeightedItem(pop= population, weights= weights)
    return choices(bereich)




for hour in range(10):
    day = DetermineDay(hour)
    pers = CalcMobilePersonen(day,1000)
    ways = CalcNumberofWays(day)
    zweck = GenerateWegZweck(day)
    artMobilitat = GenerateIfDriving(zweck)
    km = GenerateKilometer()