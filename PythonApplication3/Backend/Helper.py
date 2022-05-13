from datetime import date
import pandas as pd
import numpy as np
#Viertelstunden Leistungswerte fur den Jahresverbrauch von 1.000 kWh pro Jahr
electricProfile = pd.read_csv("./Data/Stromprofil.csv", delimiter=";", decimal = ",")
time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

Spring = date(2022,3,21) 
Summer = date(2022,6,19)
Autumn = date(2022,9,17)
Winter = date(2022,12,21)

def GetStromProfil(hour):
	"""Nimmt eine Stunde und gibt den Stromverbrauch zuruck
	Dabei wird nach Jahreszeiten unterschieden
	Die Werte werden prozentuell aufgeteilt um scharfe Kanten im Verbrauch zu vermeiden"""

	mode = IsWeekday2(hour)

	Date1 = date(time[hour].year,time[hour].month,time[hour].day)
	if Spring <= Date1 <= Summer:
		diffSpring = (Date1 - Spring).days
		diffSummer = (Summer - Date1).days
		diffSpringPercent = 1 - diffSpring / (diffSummer + diffSpring)
		diffSummerPercent = 1 - diffSummer / (diffSummer + diffSpring)
		hour = DetermineHourofDay(hour)
		strom = electricProfile[mode + "_Sommer"][hour*4:hour*4+4].mean() * diffSummerPercent + \
			electricProfile[mode + "_Ubergang"][hour*4:hour*4+4].mean() * diffSpringPercent
		#print("Spring-Summer")
		return strom

	elif Summer <= Date1 <= Autumn:
		diffSummer = (Date1 - Summer).days
		diffAutumn = (Autumn - Date1).days
		diffSummerPercent = 1 - diffSummer / (diffSummer + diffAutumn)
		diffAutumnPercent = 1 - diffAutumn / (diffSummer + diffAutumn)
		hour = DetermineHourofDay(hour)
		strom = electricProfile[mode + "_Sommer"][hour*4:hour*4+4].mean() * diffSummerPercent + \
			electricProfile[mode + "_Ubergang"][hour*4:hour*4+4].mean() * diffAutumnPercent
		#print("Summer-Autumn")
		return strom

	elif Autumn <= Date1 <= Winter:
		diffAutumn = (Date1 - Autumn).days
		diffWinter = (Winter - Date1).days
		diffAutumnPercent = 1 - diffAutumn / (diffWinter + diffAutumn)
		diffWinterPercent = 1 - diffWinter / (diffWinter + diffAutumn)
		hour = DetermineHourofDay(hour)
		strom = electricProfile[mode + "_Winter"][hour*4:hour*4+4].mean() * diffWinterPercent + \
			electricProfile[mode + "_Ubergang"][hour*4:hour*4+4].mean() * diffAutumnPercent
		#print("Autumn-Winter")
		return strom

	else:
		if Date1 >= Winter:
			diffWinter = (Date1 - Winter).days
			diffSpring = 365 - abs(Spring - Date1).days
		
		if Date1 <= Spring:
			diffWinter = 365 - abs(Date1 - Winter).days
			diffSpring = (Spring - Date1).days
	
		diffSpringPercent = 1 - diffSpring / (diffSpring + diffWinter)
		diffWinterPercent = 1 - diffWinter / (diffSpring + diffWinter)

		hour = DetermineHourofDay(hour)
		strom = electricProfile[mode + "_Winter"][hour*4:hour*4+4].mean() * diffWinterPercent + \
			electricProfile[mode + "_Ubergang"][hour*4:hour*4+4].mean() * diffSpringPercent
		#print("Winter-Spring")
		return strom

def DetermineHourofDay(hour):
	return (hour) % 24

def IsWeekday2(hour):
	if time[hour].weekday() == 5:
		return "Samstag"
	elif time[hour].weekday() == 6:
		return "Sonntag"
	else:
		return "Werktag"

def IsWeekday(hour):
	if time[hour].weekday() == 6 or time[hour].weekday() == 5:
		return False
	else:
		return True




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




