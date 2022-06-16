
import pandas as pd
from pandas.core.frame import DataFrame


def DefinePV(name: str) -> DataFrame:    
    return pd.read_csv(f"./Data/PV.csv", decimal=",", sep=";")[name].to_list()  #in kWh

#Strombedarf ist auf 1 kWh genormt
Strombedarf = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")
Strombedarf["WP"] = pd.read_csv("./Ergebnis/Strombedarf_WP.csv", decimal=",", sep=";")["Strombedarf_WP"]
#Bedarf_Schule = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Schule"].to_list()  #in kWh
#Bedarf_Gewerbe = pd.read_csv("./Data/Strombedarf.csv", decimal=",", sep=";")["Gewerbe"].to_list()  #in kWh


wohnen = 1488565
gewerbe = 514674
schule = 300104

Strombedarf["Wohnen"] = Strombedarf["Wohnen"] * wohnen
Strombedarf["Gewerbe"] = Strombedarf["Gewerbe"] * gewerbe
Strombedarf["Schule"] = Strombedarf["Schule"] * schule

