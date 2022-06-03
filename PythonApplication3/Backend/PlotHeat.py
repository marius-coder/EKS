# -*- coding: cp1252 -*-


import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
import bokeh
import pandas as pd
import numpy as np

time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

def PlotspezVerbrauch(dicBuildings):
    fig, ax = plt.subplots()    

    dic = {}

    for key,building in dicBuildings.items():
        dic[key] = abs(sum([qHL for qHL in building.DF.qHL if qHL <= 0 ]) / building.gfa)


    toPlot = pd.DataFrame(dic, index = ['W1', 'W2', 'W3', 'W4'])

    sns.barplot(data=toPlot, ax = ax)
    
    fig.suptitle('Spezifischer Heizwärmebedarf der Gebäude', fontsize=16)
    ax.set_xlabel('Gebäude')
    ax.set_ylabel('spezifische Heizwärmebedarf [kWh/m²a]')
    plt.show()


def PlotWochenVerbrauch(data):
    fig, ax = plt.subplots()    

    toPlot = pd.DataFrame({ "W1" : data["W1"].DF.qHL,
                            "W2" : data["W2"].DF.qHL,
                            "W3" : data["W3"].DF.qHL,
                            "W4" : data["W4"].DF.qHL,
                            })

    timePlot = time[0:len(data["W1"].DF.qHL)]
    toPlot = toPlot.set_index(timePlot)
    toPlot = toPlot.resample("d").sum()
    toPlot = toPlot.resample("w").mean()

    sns.barplot(data=toPlot, ax = ax)
    
    fig.suptitle('Gesammelter Status aller Autos', fontsize=16)
    ax.legend(loc='upper left')
    ax.set_xlabel('Stunde [h]')
    ax.set_ylabel('Anzahl Autos')
    plt.show()

