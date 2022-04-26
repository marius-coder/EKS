
import pandas as pd
import numpy as np
from datetime import date
from Backend.Helper import *

electricProfile = pd.read_csv("./Data/Stromprofil.csv", delimiter=";", decimal = ",")
time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

Spring = date(2022,3,21)
Summer = date(2022,6,19)
Autumn = date(2022,9,17)
Winter = date(2022,12,21)

hour = 8600

Date1 = date(time[hour].year,time[hour].month,time[hour].day)


if Spring <= Date1 <= Summer:
	diffSpring = (Date1 - Spring).days
	diffSummer = (Summer - Date1).days
	diffSpringPercent = 1 - diffSpring / (diffSummer + diffSpring)
	diffSummerPercent = 1 - diffSummer / (diffSummer + diffSpring)
	hour = DetermineHourofDay(hour)
	strom = electricProfile["Werktag_Sommer"][hour*4] * diffSummerPercent + electricProfile["Werktag_Ubergang"][hour*4] * diffSpringPercent
	print("Spring-Summer")
	return strom

elif Summer <= Date1 <= Autumn:
	diffSummer = (Date1 - Summer).days
	diffAutumn = (Autumn - Date1).days
	diffSummerPercent = 1 - diffSummer / (diffSummer + diffAutumn)
	diffAutumnPercent = 1 - diffAutumn / (diffSummer + diffAutumn)
	hour = DetermineHourofDay(hour)
	strom = electricProfile["Werktag_Sommer"][hour*4] * diffSummerPercent + electricProfile["Werktag_Ubergang"][hour*4] * diffAutumnPercent
	print("Summer-Autumn")
	return strom

elif Autumn <= Date1 <= Winter:
	diffAutumn = (Date1 - Autumn).days
	diffWinter = (Winter - Date1).days
	diffAutumnPercent = 1 - diffAutumn / (diffWinter + diffAutumn)
	diffWinterPercent = 1 - diffWinter / (diffWinter + diffAutumn)
	hour = DetermineHourofDay(hour)
	strom = electricProfile["Werktag_Winter"][hour*4] * diffWinterPercent + electricProfile["Werktag_Ubergang"][hour*4] * diffAutumnPercent
	print("Autumn-Winter")
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
	strom = electricProfile["Werktag_Winter"][hour*4] * diffWinterPercent + electricProfile["Werktag_Ubergang"][hour*4] * diffSpringPercent
	print("Winter-Spring")
	return strom

