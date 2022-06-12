# -*- coding: cp1252 -*-
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np



def PlotEigenVerbrauch(DS):

	fig, ax = plt.subplots(3,2,figsize=(10,12),gridspec_kw={'width_ratios': [2, 1]})

    for key,val in DS.items():

        charge = DS.data[]["CarToBuilding"]
        discharge = DS.data[]["energyPvToCar"]

	    verlustLaden = charge * (1-car.effizienz)
        vorFahren = charge - verlustLaden

        nachFahren = discharge / car.effizienz
        verlustEntladen = nachFahren * (1-car.effizienz)
        nachFahrenEntladen = nachFahren - verlustEntladen
        verlustGesamt = verlustEntladen + verlustLaden
        Fahrverbrauch = vorFahren - nachFahren

        labels = ["Verbrauch durch Gebäude", "Verbrauch durch Fahren","Lade/Entladeverluste"]
        sizes = [nachFahrenEntladen, Fahrverbrauch, verlustGesamt]    

        fig.suptitle('Aufteilung der zwischengespeicherten Energie', fontsize=18)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.show()
