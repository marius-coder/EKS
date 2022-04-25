
import pandas as pd
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt
import importlib
from bokeh.plotting import figure, show
import ErdSimCPP
from timeit import default_timer as timer

from EMS_Backend.Classes.Building import Building
from EMS_Backend.Classes.Wärmespeicher import Wärmespeicher
from EMS_Backend.Classes.Wärmepumpe import Wärmepumpe
from EMS_Backend.Classes.Stromnetz import Stromnetz
from EMS_Backend.Classes.Erdwärme import BKA
import EMS_Backend.Classes.Import as Import

class Simulation():

	def __init__(self):		 
		 self.building = Building("./EMS_Backend/data/building.xlsx")
		 self.df_usage = pd.read_csv("./EMS_Backend/data/usage_profiles.csv", encoding="cp1252")
		 self.ta = np.genfromtxt("./EMS_Backend/data/climate.csv", delimiter=";", usecols = (1), skip_header = 1) #°C
		 self.qsolar = np.genfromtxt("./EMS_Backend/data/Solar_gains.csv") #W/m² Solar gains
		 self.import_data = Import.importGUI
		 self.warmwater_data = self.import_data.input_Warmwater
		 self.PV_Bat_data = self.import_data.input_PV_Batterie
		 self.WP_Heizen = self.import_data.input_WP_Heizen
		 self.speicher_HZG = self.import_data.input_Speicher_HZG
		 self.WP_WW = self.import_data.input_WP_WW
		 self.speicher_WW = self.import_data.input_Speicher_WW

	def Setup_Simulation(self):
		""" """
		self.qi_winter = self.df_usage["Qi Winter W/m²"].to_numpy()
		self.qi_sommer = self.df_usage["Qi Sommer W/m²"].to_numpy()
		self.qi = self.qi_winter                                 #Interne Gewinne als Kombination von Sommer und Winter, f�rs erste = QI_winter
		self.ach_v = self.df_usage["Luftwechsel_Anlage_1_h"].to_numpy() #Air change per hour through ventilation
		self.ach_i = self.df_usage["Luftwechsel_Infiltration_1_h"].to_numpy() #Air change per hour through infiltration
		self.anz_personen = self.df_usage["Pers/m2"] 
		self.q_warmwater = np.zeros(8760)
		self.q_maschinen = self.df_usage['Aufzug, Regelung etc._W_m2']
		self.q_beleuchtung = self.df_usage["Beleuchtung_W_m2"]
		self.Pel_gebäude = np.zeros(8760)

		self.qv = np.zeros(8760)        #Ventilation losses
		self.qt = np.zeros(8760)        #transmission losses
		self.ti = np.zeros(8760)        #indoor temperature
		self.ti_sim = 20                #Laufvariable für die Innentemperatur
		self.qh = np.zeros(8760)        #Heating demand
		self.qc = np.zeros(8760)        #cooling demand
		self.CONST_Q_PERSONEN_SPEZ = 80 #W/Person
		self.cp_air = 0.34  # spez. Wärme kapazität * rho von Luft (Wh/m3K)

		self.t_Zul = np.ones(8760) #Zulufttemperatur
		self.t_Abl = np.ones(8760) #Ablufttemperatur
		self.t_soll = np.ones(8760) * 20   #Soll Rauminnentemperatur
		self.qs = np.zeros(8760) #Solar gains array in Watt
		self.q_außen = np.zeros(8760)
		self.q_personen = np.zeros(8760)
		self.q_beleuchtung = np.zeros(8760)
		self.q_maschinen = np.zeros(8760)
		self.q_innen = np.zeros(8760)
		self.t_heating = 20
		self.t_cooling = 26
		self.b_heating = True
		
		self.t_hzg_VL = 30
		self.t_hzg_RL = 25
		self.t_klg_VL = 8
		self.t_klg_RL = 12
		self.t_WW_VL = 50

		self.Speicher_HZG = Wärmespeicher(self.speicher_HZG, self.t_hzg_VL, self.t_hzg_RL)
		self.WP_HZG = Wärmepumpe(speicher = self.Speicher_HZG,data_WP = self.WP_Heizen, geb_VL_HZG = self.t_hzg_VL, geb_VL_KLG = self.t_klg_VL)


		self.Speicher_WW = Wärmespeicher(self.speicher_WW, self.t_WW_VL, 30)
		self.WP_WW = Wärmepumpe(speicher = self.Speicher_WW,data_WP = self.WP_WW, geb_VL_HZG = self.t_WW_VL, geb_VL_KLG = 0)
		self.Stromnetz = Stromnetz(self.PV_Bat_data)

		#Mehrmals derselbe Input wegen Tech Debt
		self.Erd_Sim = BKA(self.import_data.input_GeoData, self.import_data.input_GeoData, self.import_data.input_GeoData)
		self.Erd_Sim.Init_Sim()
		self.Erd_SimCPP = ErdSimCPP.ErdSim(self.import_data.input_GeoData, self.import_data.input_GeoData, self.import_data.input_GeoData)
		
		self.li_timePython = []
		self.li_timeCPP = []
		self.li_Sondenfeld = []
		self.li_speicherTemperatur_HZG = []
		self.li_speicherTemperatur_WW = []

		self.stat_HL = self.Static_HL()
		self.stat_KL = self.Static_KL()

		self.heating_months = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]
		self.cooling_months = [7, 8]

		self.fehler_HZG_Speicher = np.zeros(8760)
		self.fehler_WW_Speicher = np.zeros(8760)
		self.fehler_Stromnetz = np.zeros(8760)

		self.li_Verluste = np.zeros(8760)
		self.li_Verluste_Speicher = np.zeros(8760)
		self.li_Laden = np.zeros(8760)
		self.li_Entladen = np.zeros(8760)

		self.li_meanTemp = np.zeros(8760)
		self.HZG_GrenzTemp = self.SetHeizgrenzTemperatur(self.stat_HL['Heizlast [W]'], self.building.fußboden["Fläche"])

		print(f"Heizgrenztemperatur: {self.HZG_GrenzTemp} °C")
		print(f"Die statische Heizlast beträgt {round(self.stat_HL['Heizlast [W]'] / 1000,2)} kW")
		print(f"Die statische Kühllast beträgt {round(self.stat_KL['Kühllast [W]'] / 1000,2)} kW")


	   
	def calc_t_Zul(self, hour):
		WRG = self.building.WRG
		self.t_Abl[hour] = self.ti[hour]
		self.t_Zul[hour+1] = self.t_Abl[hour] * WRG + self.t_Abl[hour] * (1 - WRG)
		print(f"Zulufttemperatur: {self.t_Zul[hour]} °C")

	def calc_QV(self, ach_v, ach_i, t_Zul, ta, ti ):
		"""Ventilation heat losses [W/m²BGF] at timestep t"""
		#Lüftungswärmeverlust-Koeffizient für mechanische Lüftung
		Hv = self.cp_air * ach_v * self.building.volumen  # W/K
		qv_mech = Hv * (t_Zul - ti) # W
		 
		#Lüftungswärmeverlust-Koeffizient für Infiltration
		Hv = self.cp_air * ach_i * self.building.volumen  # W/K
		qv_inf = Hv * (ta - ti) # W

		#Gesamtlüftungsverluste in Watt
		qv = (qv_mech + qv_inf)
		return qv
	 

	def calc_QT(self, ta, ti):
		"""Transmission heat losses [W/m²BGF] at timestep t"""
		#Transmisisonsverlust von beheizten Raum an die Außenluft eg. Wand und Dach
		dTa = ta - ti
		q_wand = self.building.wand["LT"] * dTa
		q_fenster = self.building.window["LT"] * dTa
		q_dach = self.building.dach["LT"] * dTa
		#Transmissionsverlust von beheizten Raum zu unbeheizten Räumen
		#N.V.

		#Transmissionsverlust von beheizten Räumen an das Erdreich
		dT_boden = 10 - ti #Annahme das der Boden konstant 10°C hat.
		q_fußboden = self.building.fußboden["LT"] * dT_boden

		#Gesamttransmissionswärmeverlust in Watt
		qt = (q_wand + q_fußboden + q_dach + q_fenster) #Watt
		return qt

		
	def handle_losses(self, t, q_toApply):
		# determine indoor temperature after losses
		self.ti_sim = self.TI_after_Q(self.ti_sim, q_toApply, self.building.heat_capacity, self.building.gfa) #°C


	def TI_after_Q(self, Ti_before, Q, cp, A):
		"""cp = spec. building heat_capacity"""
		return Ti_before + Q / A / cp

	def heating_power(self, ti_s, ti, cp, A):
		return cp * A * (ti_s - ti)

	def Static_HL(self):
		min_ta = min(self.ta)
		ti = max(self.t_soll)
		max_achi = max(self.ach_i)
		max_achv = max(self.ach_v)
		t_Zul = min_ta

		qt = self.calc_QT(min_ta, ti)
		qv = self.calc_QV(max_achv, max_achi, t_Zul, min_ta, ti )
		
		stat_HL = {
			"Heizlast [W]" : qt + qv,
			"spez. Heizlast [W/m²]" : (qt + qv) / self.building.gfa
			}
		return stat_HL


	def Q_Personen(self, hour) -> float:
		return self.anz_personen[hour] * self.building.gfa * self.CONST_Q_PERSONEN_SPEZ #W

	def Q_Beleuchtung(self, hour) -> float:
		return self.building.gfa * self.q_beleuchtung[hour]
	
	def Q_Maschinen(self, hour) -> float:
		return self.building.gfa * self.q_maschinen[hour]

	def Q_Solar(self, hour) -> float:
		return self.qsolar[hour] * self.building.window["Fläche"]

	def Q_InnerGains(self, hour) -> float:
		return self.qi[hour] * self.building.gfa

	def Static_KL(self):
		max_value = max(self.ta)
		hour = list(self.ta).index(max_value)

		#Kühllast von Außen
		qt = self.calc_QT(self.ta[hour], 26) #W
		qv = self.calc_QV(self.ach_v[hour], self.ach_i[hour], self.t_soll[hour], self.ta[hour], 26 ) #W
		qs = self.Q_Solar(hour)
		q_außen = qt + qv + qs #W

		#Innere Kühllast
		q_personen = self.Q_Personen(hour)
		q_beleuchtung = self.Q_Beleuchtung(hour)
		q_maschinen = self.Q_Maschinen(hour)
		q_innen = q_personen + q_beleuchtung + q_maschinen

		#gesamte Kühllast
		stat_KL = {
			"Kühllast [W]" : q_außen + q_innen,
			"spez. Kühllast [W/m²]" : (q_außen + q_innen) / self.building.gfa
			}
		return stat_KL

	def Simulate(self):
		for hour in range(8760):		
			
			#Zulufttemperatur rechnen
			self.calc_t_Zul(hour-1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------    
			#Heiz / Kühllast berechnen
			#Äußere Wärmeströme
			self.qt[hour] = self.calc_QT( self.ta[hour], self.ti_sim) #Transmission
			self.qv[hour] = self.calc_QV( self.ach_v[hour], self.ach_i[hour], self.t_Zul[hour], self.ta[hour], self.ti_sim) #Ventilation
			self.qs[hour] = self.Q_Solar(hour) #Solare Gewinne
			self.q_außen[hour] = self.qt[hour] + self.qv[hour] + self.qs[hour] #W Gesamt

			#Innere Wärmeströme
			self.q_personen[hour] = self.Q_Personen(hour)
			self.q_beleuchtung[hour] = self.Q_Beleuchtung(hour)
			self.q_maschinen[hour] = self.Q_Maschinen(hour)
			self.q_innen[hour] = self.q_personen[hour] + self.q_beleuchtung[hour] + self.q_maschinen[hour]

			#Gesamtwärmeströme
			self.q_gesamt = self.q_außen[hour] + self.q_innen[hour]
			self.handle_losses(hour, q_toApply = self.q_gesamt) #Neue Innentemperatur rechnen
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			print("Stunde: ",hour)
			print("Verluste: ",self.q_gesamt)
			print(f"Tsim: {self.ti_sim}")
			print("Temp vor Heizen: ",self.ti_sim)
			self.ti[hour] = self.ti_sim

			self.WP_HZG.COP_betrieb[hour] = self.WP_HZG.GetCOP(self.ta[hour])
			#print(f"COP Heizen bei {self.ta[hour]} °C Außentemperatur: {self.WP_HZG.COP_betrieb[hour]}")

			#if DetermineMonth(hour) == 2:
			#	print(f"Gesamt Verluste: {sum(self.li_Verluste) / 1000} kW")
			#	print(f"Gesamt Laden: {sum(self.li_Laden) / 1000} kW")
			#	print(f"Gesamt Entladen: {sum(self.li_Entladen) / 1000} kW")
			#	print(f"Gesamt Speicherverluste: {sum(self.li_Verluste_Speicher) / 1000} kW")


			self.li_meanTemp[hour] = self.GetMeanTemp(hour)
			#Heizen
			self.Q_entladen_HZG = 0
			
			#Verlust und Ausgleichsvorgänge
			self.WP_HZG.speicher.UpdateSpeicher(hour, self.WP_HZG.WP_VL_HZG)
			if DetermineMonth(hour) in self.heating_months:
				self.t_soll[hour] = self.building.TsWinter
				#Check_SpeicherHeizen kontrolliert die Speichertemperatur und führt die Verlustvorgänge für den Speicher durch
				#Wenn notwendig schaltet diese Funktion auch die WP ein
				self.WP_HZG.Check_SpeicherHeizen(hour)

				if self.WP_HZG.is_on[hour] == True:
					self.WP_HZG.Pel_Betrieb[hour] = self.WP_HZG.Pel
				else:
					self.WP_HZG.Pel_Betrieb[hour] = 0
				#Benötigte Wärmeenergie um auf Solltemperatur zu kommen
				self.q_soll = self.heating_power(self.t_soll[hour], self.ti_sim, self.building.heat_capacity, self.building.gfa)
				self.qh[hour] = self.q_soll

				#Energie aus dem Speicher entnehmen
				if self.WP_HZG.speicher.li_schichten[-1]["Temperatur [°C]"] > self.t_hzg_VL:
					self.Q_entladen_HZG = self.q_soll
					self.WP_HZG.speicher.Speicher_Entladen(Q_Entladen = self.q_soll, RL = self.t_hzg_RL)
					#Neue Innentemperatur berechnen
					self.handle_losses(hour, q_toApply = self.q_soll)



			elif DetermineMonth(hour) in self.cooling_months:
				self.t_soll[hour] = self.building.TsSommer
				#Check_SpeicherKühlen kontrolliert die Speichertemperatur und führt die Verlustvorgänge für den Speicher durch
				#Wenn notwendig schaltet diese Funktion auch die WP ein
				self.WP_HZG.Check_SpeicherKühlen(hour)

				if self.WP_HZG.is_on[hour] == True:
					self.WP_HZG.Pel_Betrieb[hour] = self.WP_HZG.Pel
				else:
					self.WP_HZG.Pel_Betrieb[hour] = 0
				#Benötigte Wärmeenergie um auf Solltemperatur zu kommen
				self.q_soll = self.heating_power(self.t_soll[hour], self.ti_sim, self.building.heat_capacity, self.building.gfa)
				self.qc[hour] = self.q_soll

				#Energie aus dem Speicher entnehmen
				if self.WP_HZG.speicher.li_schichten[-1]["Temperatur [°C]"] < self.t_klg_VL:
					self.Q_entladen_HZG = self.q_soll
					self.WP_HZG.speicher.Speicher_Entladen(Q_Entladen = self.q_soll, RL = self.t_hzg_RL)
					#Neue Innentemperatur berechnen
					self.handle_losses(hour, q_toApply = self.q_soll)
			print("Temp nach Heizen: ",self.ti_sim)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------		
			#Warmwasser
			month = DetermineMonth(hour)
			hourofDay = DetermineHourofDay(hour)

			#Verlust und Ausgleichsvorgänge
			self.WP_WW.speicher.UpdateSpeicher(hour, self.WP_WW.WP_VL_HZG)

			self.Q_entladen_WW = 0
			self.WP_WW.COP_betrieb[hour] = self.WP_WW.GetCOP(self.ta[hour])
			#print(f"COP Warmwasser bei {self.ta[hour]} °C Außentemperatur: {self.WP_WW.COP_betrieb[hour]}")
			Q_warmwater = self.CalcWarmwaterEnergy(month, hourofDay)
			self.q_warmwater[hour] = Q_warmwater
			print(f"Benötigte Warmwasserleistung: {Q_warmwater/1000} kW")
			#Check_SpeicherHeizen kontrolliert die Speichertemperatur und führt die Verlustvorgänge für den Speicher durch
			#Wenn notwendig schaltet diese Funktion auch die WP ein
			self.WP_WW.Check_SpeicherHeizen(hour)

			if self.WP_WW.is_on[hour] == True:
				self.WP_WW.Pel_Betrieb[hour] = self.WP_WW.Pel
			else:
				self.WP_WW.Pel_Betrieb[hour] = 0
			#Energie aus dem Speicher entnehmen
			if self.WP_WW.speicher.li_schichten[-1]["Temperatur [°C]"] > self.t_WW_VL:
				self.Q_entladen_WW = self.q_warmwater[hour]
				self.WP_WW.speicher.Speicher_Entladen(Q_Entladen = self.q_warmwater[hour], RL = 15)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			#Strom			
			self.Pel_gebäude[hour] = self.CalcStrombedarf(hour, month, hourofDay)
			print(f"Benötigte Stromleistung: {self.Pel_gebäude[hour]/1000} kW")
			reslast = self.Stromnetz.CalcResLast(hour,self.Pel_gebäude[hour])
			self.Stromnetz.CheckResLast(hour,reslast)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			#Simulation-Bodenerwärmung Python
			if DetermineMonth(hour) in self.heating_months:
				Q_toDump = self.Q_entladen_WW * -1 + self.Q_entladen_HZG * -1

			elif DetermineMonth(hour) in self.cooling_months:
				Q_toDump = self.WP_WW.Pel_Betrieb[hour] + self.WP_HZG.Pel_Betrieb[hour] +\
							self.Q_entladen_WW + self.Q_entladen_HZG 
			if self.import_data.input_GeoData["Typ"] == "Python":
				start = timer()
				self.Erd_Sim.Simulate(Q_toDump)
				end = timer()
				print(f"Python: {end - start} Sekunden")
				self.li_timePython.append(end - start)
				self.li_Sondenfeld.append(self.Erd_Sim.Get_Attr_List("temperatur"))
			
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			#Simulation-Bodenerwärmung C++		
			elif self.import_data.input_GeoData["Typ"] == "CPP":	
				start = timer()
				#da = pybind11module.ErdSim(data_Sim, data_Pixel, data_Boden)
				self.Erd_SimCPP.Simulate(Q_toDump)
				end = timer()
				Erd_Sim_Temps = self.Erd_SimCPP.GetTemperatures()
				print(f"C++: {end - start} Sekunden")
				self.li_timeCPP.append(end - start)
				self.li_Sondenfeld.append(Erd_Sim_Temps)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			#Bilanzgrenzentest
			self.li_speicherTemperatur_HZG.append(self.WP_HZG.speicher.GetSpeicherTemperaturen())
			self.li_speicherTemperatur_WW.append(self.WP_WW.speicher.GetSpeicherTemperaturen())

			self.fehler_HZG_Speicher[hour] = TestBilanzgrenze(li_input = [self.WP_HZG.Q_toLoad],
															li_output = [self.Q_entladen_HZG,self.WP_HZG.speicher.q_trans_Sum])
			self.fehler_WW_Speicher[hour] = TestBilanzgrenze(li_input = [self.WP_WW.Q_toLoad],
															li_output = [self.Q_entladen_WW,self.WP_WW.speicher.q_trans_Sum])
			self.fehler_Stromnetz[hour] = TestBilanzgrenze(li_input = [self.Stromnetz.Batterieeinspeisung[hour]],
															li_output = [self.Stromnetz.Batterieentladung[hour],self.Stromnetz.Batterie.Verluste[hour]])
			self.li_Verluste[hour] = Q_warmwater
			self.li_Verluste_Speicher[hour] = self.WP_WW.speicher.q_trans_Sum
			self.li_Laden[hour] = self.WP_WW.Q_toLoad
			self.WP_WW.Q_toLoad = 0
			self.li_Entladen[hour] = self.Q_entladen_WW

			print("---------------------------------------------------------------")
		print(f"Gesamt Verluste: {sum(self.li_Verluste) / 1000} kW")
		print(f"Gesamt Laden: {sum(self.li_Laden) / 1000} kW")
		print(f"Gesamt Entladen: {sum(self.li_Entladen) / 1000} kW")
		print(f"Gesamtfehler Heizen: {sum(self.fehler_HZG_Speicher) / 1000} kW")
		print(f"Gesamtfehler Warmwasser: {sum(self.fehler_WW_Speicher) / 1000} kW")
		print(f"Gesamtfehler Batterie: {sum(self.fehler_Stromnetz) / 1000} kW")
		print(f"MAXIMALE TEMPERATUR: {max(self.ti)}")
		print(f"MINIMALE TEMPERATUR: {min(self.ti)}")
		#print(f"Mean Python: {np.mean(self.li_timePython)}")
		#print(f"std Python: {np.std(self.li_timePython)}")
		#print(f"Mean C++: {np.mean(self.li_timeCPP)}")
		#print(f"std C++: {np.std(self.li_timeCPP)}")
		#plt.clf()
		#sns.heatmap(test, square=True, cbar_kws={'label': 'Temperatur [°C]'})
		#plt.title("Temperaturfeld der Erdwärmesonden")
		#plt.show()




			
	def CalcWarmwaterEnergy(self, month, hourofDay):
		m_water = self.import_data.input_Warmwater["hour [l/h]"][month-1][hourofDay]  #liter
		print(f"Warmwasserverbauch in liter: {m_water}")
		Q_waterheating = m_water * 4180 * (self.t_WW_VL-15) /3600
		return Q_waterheating

	def CalcStrombedarf(self, hour, month, hourofDay):
		"""Diese Funktion nimmt das importierte Stromprofil, extrahiert den Strombedarf und addiert extra Verbraucher dazu 
		(Die beiden Wärmepumpen)"""

		#Profilentnahme
		P_profile = self.import_data.input_Strombedarf["hour [kWh/h]"][month-1][hourofDay] * 1000  #Watt
		#Hinzufügen der Wärmepumpen
		P_profile += self.WP_HZG.Pel_Betrieb[hour] + self.WP_WW.Pel_Betrieb[hour]
		return P_profile

	def GetMeanTemp(self, hour):
		"""Diese Funktion gibt die Mittlere Tagesaußentemperatur zurück
			Mit dieser soll bestimmt werden ob geheizt oder gekühlt werden soll"""
		#Errorcheck BAD HACK
		#Zum glück muss man in den ersten zwei Jännerwochen immer heizen
		if hour < 360:
			return 0
		meanTemp = np.mean(self.ta[hour - 360:hour])

		return meanTemp

	def SetHeizgrenzTemperatur(self, HL, fläche):
		HL_spez = abs(HL) / fläche

		if 120 < HL_spez: #W/m² Altbau vor 1977
			return 18 #°C
		elif 80 < HL_spez < 120: #W/m² Altbau von 1977 bis 1995
			return 17 #°C
		elif 60 < HL_spez < 80: #W/m² Altbau von 1995 bis 2002
			return 16 #°C
		elif 40 < HL_spez < 60: #W/m² Gebäude nach EnEV
			return 15 #°C
		elif 20 < HL_spez < 40: #W/m² Niedrigenergiehaus
			return 14 #°C
		elif 0 < HL_spez < 20: #W/m² Passivhaus
			return 13 #°C



def DetermineHourofDay(hour):
	return (hour+1) % 24


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

def TestBilanzgrenze(li_input, li_output):
	var_input = 0
	var_output = 0
	for var_in,var_out in zip(li_input,li_output):
		var_input += abs(var_in)
		var_output += abs(var_out)
	return var_input - var_output







#model = Simulation(b_geothermal = False)
#model.Setup_Simulation()
#model.Simulate()

