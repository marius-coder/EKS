
import pandas as pd



PV = pd.read_csv("./Data/PV.csv", usecols = [1], decimal=",", sep=";")["AC Production"].to_list()  #in kWh

#Strombedarf ist auf 1 kWh genormt
Strombedarf = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")
#Bedarf_Schule = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Schule"].to_list()  #in kWh
#Bedarf_Gewerbe = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Gewerbe"].to_list()  #in kWh


wohnen = 1488565
Strombedarf["Wohnen"] = Strombedarf["Wohnen"] * wohnen
