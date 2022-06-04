
import pandas as pd
import numpy as np
import math
from Helper import *


class HL():      
    
    def InitHeizlast(self):
    	self.belegungPersonen = pd.read_csv("./Data/Profile_PersonenGewinne.csv", delimiter=";")
    	self.gewinnePersonen = 80 #W/Person
    	self.qsolar = np.genfromtxt("./Data/Solar_gains.csv") #W/m² Solar gains
    	self.infiltration = pd.read_csv("./Data/usage_profiles.csv", encoding="cp1252")["Luftwechsel_Infiltration_1_h"]


    def calc_t_Zul(self, ta):
        WRG = self.WRG / 100
        t_Abl = self.ti
        return t_Abl * WRG + ta * (1 - WRG)

    def calc_QV(self, ta, hour):
    		"""Ventilationswärmeverlust nach ÖNORM H 7500-1:2015"""

            #Hygienischer Lüftungswechsel
    		V_hyg_min = self.volumen * self.Luftwechsel
    		 
    		Hv = self.cp_air * V_hyg_min  # W/K
            #Gesamtlüftungsverluste in Watt
    		qv = Hv * (self.calc_t_Zul(ta) - self.ti) # Watt

    		V_inf =  self.infiltration[hour] * self.volumen

    		Hinf = self.cp_air * V_inf  # W/K
    		#Gesamtlüftungsverluste in Watt
    		qinf = Hinf * (ta - self.ti) # Watt
    		qGes = qv + qinf
    		return qGes / self.gfa
    	 
    def calc_QT_Wand(self, ta):
        #Transmisisonsverlust von beheizten Raum an die Außenluft eg. Wand und Dach
        dTa = ta - self.ti
        q_wand = self.wand["LT"] * dTa
        q_fenster = self.fenster["LT"] * dTa        
        return q_wand + q_fenster
    
    def calc_QT_Dach(self,ta):
      		dTa = ta - self.ti
      		q_dach = self.dach["LT"] * dTa            
      		return q_dach
              
    def calc_QT_Boden(self,ta):
      		q_boden = self.boden["LT"] * (6.3 - self.ti) #6 Grad aus Norm bezogen            
      		return q_boden
    
    def calc_QT_Sum(self, ta):
      		"""Transmissionswärmeverlust nach ÖNORM H 7500-1:2015"""
      		if ta > self.ti:
    		    return 0

      		q_boden = self.calc_QT_Boden(ta)
      		q_dach = self.calc_QT_Dach(ta)            
      		q_wand = self.calc_QT_Wand(ta)
      		return (q_wand + q_dach + q_boden) / self.gfa


    def DetermineBelegung(self, hour):
        hourofDay = DetermineHourofDay(hour)
        if IsWeekday(hour):
            return self.belegungPersonen["Belegung_Werktag [%]"][hourofDay] / 100
        else:
            return self.belegungPersonen["Belegung_Wochenende [%]"][hourofDay] / 100

    def calc_Maschinen(self, strom):
        return strom * 0.5 / self.gfa

    def calc_Personen(self, hour, anz_Personen):
        belegung = self.DetermineBelegung(hour)
        return self.gewinnePersonen * anz_Personen * belegung / self.gfa

    def CalcThermalFlows(self, ta, hour, anz_Personen, strom):
        """ Returns Watts
        Diese Wrapperfunktion callt alle unterfunktionen um alle thermischen Energieflüsse
            eines Gebäudes zu berechnen."""
        qT = self.calc_QT_Sum(ta) 
        qV = self.calc_QV(ta, hour)
        #print(f"spez. Heizlast: {(qT+qV)/self.gfa} W/m²")
        qI = self.calc_Personen(hour = hour, anz_Personen = anz_Personen)
        qM = self.calc_Maschinen(strom) * 1000
        qS = self.qsolar[hour]
        qSum = qT+qV+qI+qS+qM
        #print(f"spez. Heizlast: {(qSum)/self.gfa} W/m²")
        return qSum

    def CalcNewTemperature(self, Q):
        self.ti = self.ti + Q / self.heat_capacity

        

    def CalcQtoTargetTemperature(self):

        if self.ti < self.TsWinter:
            return self.heat_capacity * (self.TsWinter - self.ti)
        elif self.ti > self.TsSommer:
            return self.heat_capacity * (self.TsSommer - self.ti)
        else:
            return 0
        


