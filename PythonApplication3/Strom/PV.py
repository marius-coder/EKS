
import pandas as pd
from pandas.core.frame import DataFrame


def DefinePV(name: str) -> DataFrame:
    return pd.read_csv(f"./Data/{name}.csv", usecols = [1], decimal=",", sep=";")["AC Production"].to_list()  #in kWh

#Strombedarf ist auf 1 kWh genormt
Strombedarf = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")
#Bedarf_Schule = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Schule"].to_list()  #in kWh
#Bedarf_Gewerbe = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Gewerbe"].to_list()  #in kWh


wohnen = 1488565
gewerbe = 514674
schule = 300104
Strombedarf["Wohnen"] = Strombedarf["Wohnen"] * wohnen
Strombedarf["Gewerbe"] = Strombedarf["Gewerbe"] * gewerbe
Strombedarf["Schule"] = Strombedarf["Schule"] * schule




