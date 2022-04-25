
import pandas as pd
import numpy as np
import math


class HL():      
    
    def calc_QV(self, ta):
    		"""Ventilationswärmeverlust nach ÖNORM H 7500-1:2015"""
    		if ta > self.ti:
    		    return 0

            #Hygienischer Lüftungswechsel
    		V_hyg_min = self.building.volumen * self.Luftwechsel
    		 
    		Hv = self.cp_air * V_hyg_min  # W/K
            #Gesamtlüftungsverluste in Watt
    		qv = Hv * (ta - self.ti) # Watt
    		return qv
    	 
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
      		q_boden = self.boden["LT"] * (ta - self.ti) #6 Grad aus Norm bezogen            
      		return q_boden
    
    def calc_QT_Sum(self, ta):
      		"""Transmissionswärmeverlust nach ÖNORM H 7500-1:2015"""
      		if ta > self.ti:
    		    return 0

      		q_boden = self.calc_QT_Boden(ta)
      		q_dach = self.calc_QT_Dach(ta)            
      		q_wand = self.calc_QT_Wand(ta)
      		return q_wand + q_dach + q_boden