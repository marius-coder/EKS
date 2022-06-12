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
    
    fig.suptitle('Spezifischer Heizw�rmebedarf der Geb�ude', fontsize=18)
    ax.set_xlabel('Geb�ude', fontsize=14)
    ax.set_ylabel('spezifischer Heizw�rmebedarf [kWh/m�a]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

def PlotspezVerbrauchKWB(dicBuildings):
    fig, ax = plt.subplots()    

    dic = {}

    for key,building in dicBuildings.items():
        dic[key] = abs(sum([qHL for qHL in building.DF.qHL if qHL >= 0 ]) / building.gfa)


    toPlot = pd.DataFrame(dic, index = ['W1', 'W2', 'W3', 'W4'])

    sns.barplot(data=toPlot, ax = ax)
    
    fig.suptitle('Spezifischer K�hlenergiebedarf der Geb�ude', fontsize=18)
    ax.set_xlabel('Geb�ude', fontsize=14)
    ax.set_ylabel('spezifischer K�hlenergiebedarf [kWh/m�a]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    ax.set_ylim([0, 35])
    plt.show()


def PlotWochenVerbrauch(data):
    fig, ax = plt.subplots()    

    toPlot = pd.DataFrame({ "W1" : data["W1"].DF.qHL,
                            "W2" : data["W2"].DF.qHL,
                            "W3" : data["W3"].DF.qHL,
                            "W4" : data["W4"].DF.qHL,
                            "G1" : data["W1"].DF.qHL,
                            "G2" : data["W2"].DF.qHL,
                            "G3" : data["W3"].DF.qHL,
                            "G4" : data["W4"].DF.qHL,
                            "S1" : data["W1"].DF.qHL,
                            "S2" : data["W2"].DF.qHL,

                            })

    timePlot = time[0:len(data["W1"].DF.qHL)]
    toPlot = toPlot.set_index(timePlot)
    toPlot = toPlot.resample("d").sum()
    toPlot = toPlot.resample("w").mean()

    sns.lineplot(data=toPlot, ax = ax)
    
    fig.suptitle('T�glicher W�rmeeintrag im Wochendurchschnitt der einzelnen Geb�ude', fontsize=18)
    ax.legend(loc='lower center', ncol = 5)
    ax.set_xlabel('Zeit [Woche]', fontsize=14)
    ax.set_ylabel('W�rmefluss [kWh/d]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

def PlotInnentemperatur(data):
    fig, ax = plt.subplots()    

    toPlot = pd.DataFrame({ "W1" : data["W1"].DF.tInnen,
                            "W2" : data["W2"].DF.tInnen,
                            "W3" : data["W3"].DF.tInnen,
                            "W4" : data["W4"].DF.tInnen,
                            "G1" : data["W1"].DF.tInnen,
                            "G2" : data["W2"].DF.tInnen,
                            "G3" : data["W3"].DF.tInnen,
                            "G4" : data["W4"].DF.tInnen,
                            "S1" : data["W1"].DF.tInnen,
                            "S2" : data["W2"].DF.tInnen,
                            })

    timePlot = time[0:len(data["W1"].DF.tInnen)]
    toPlot = toPlot.set_index(timePlot)
    #toPlot = toPlot.resample("d").sum()
    #toPlot = toPlot.resample("w").mean()

    sns.lineplot(data=toPlot, ax = ax)
    
    fig.suptitle('Innentempemperatur der einzelnen Geb�ude', fontsize=18)
    ax.legend(loc='upper left', ncol = 2)
    ax.set_xlabel('Zeit [h]', fontsize=14)
    ax.set_ylabel('Innentemperatur [�C]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

