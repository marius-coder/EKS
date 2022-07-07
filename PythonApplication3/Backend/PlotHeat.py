# -*- coding: cp1252 -*-


import seaborn as sns
import matplotlib.pyplot as plt
from Helper import DetermineMonth
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
        inter = [0]*8760
        
        for hour in range(8760):
            if DetermineMonth(hour) < 6 or DetermineMonth(hour) > 8:
                if building.DF.qHL[hour] < 0:
                    inter[hour] = abs(building.DF.qHL[hour]) / building.gfa
        dic[key] = sum(inter)

    toPlot = pd.DataFrame({ "W1" : dic["W1"],
                            "W2" : dic["W2"],
                            "W3" : dic["W3"],
                            "W4" : dic["W4"],
                            "G1" : dic["G1"],
                            "G2" : dic["G2"],
                            "G3" : dic["G3"],
                            "G4" : dic["G4"],
                            "S1" : dic["S1"],
                            "S2" : dic["S2"],

                            }, index = ['W1', 'W2', 'W3', 'W4','G1', 'G2', 'G3', 'G4','S1', 'S2'])

    sns.barplot(data=toPlot, ax = ax)
    
    fig.suptitle('Spezifischer Heizwärmebedarf der Gebäude', fontsize=18)
    ax.set_xlabel('Gebäude', fontsize=14)
    ax.set_ylabel('spezifischer Heizwärmebedarf [kWh/m²a]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.set_ylim([0, 60])
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

def PlotspezVerbrauchKWB(dicBuildings):
    fig, ax = plt.subplots()    

    dic = {}

    for key,building in dicBuildings.items():
        inter = [0]*8760
        if hasattr(building, 'WP_HZG'):
            for hour in range(8760):
                if DetermineMonth(hour) < 6 or DetermineMonth(hour) > 8:
                    pass
                else:
                    if building.DF.qHL[hour] > 0:
                        inter[hour] = abs(building.DF.qHL[hour]) / building.gfa
        dic[key] = sum(inter)


    toPlot = pd.DataFrame({ "W1" : dic["W1"],
                            "W2" : dic["W2"],
                            "W3" : dic["W3"],
                            "W4" : dic["W4"],
                            "G1" : dic["G1"],
                            "G2" : dic["G2"],
                            "G3" : dic["G3"],
                            "G4" : dic["G4"],
                            "S1" : dic["S1"],
                            "S2" : dic["S2"],

                            }, index = ['W1', 'W2', 'W3', 'W4'])

    sns.barplot(data=toPlot, ax = ax)
    
    fig.suptitle('Spezifischer Kühlenergiebedarf der Gebäude', fontsize=18)
    ax.set_xlabel('Gebäude', fontsize=14)
    ax.set_ylabel('spezifischer Kühlenergiebedarf [kWh/m²a]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    ax.set_ylim([0, 60])
    plt.show()


def PlotWochenVerbrauch(data):
    fig, ax = plt.subplots()    

    toPlot = pd.DataFrame({ "W1" : data["W1"].DF.qHL,
                            "W2" : data["W2"].DF.qHL,
                            "W3" : data["W3"].DF.qHL,
                            "W4" : data["W4"].DF.qHL,
                            "G1" : data["G1"].DF.qHL,
                            "G2" : data["G2"].DF.qHL,
                            "G3" : data["G3"].DF.qHL,
                            "G4" : data["G4"].DF.qHL,
                            "S1" : data["S1"].DF.qHL,
                            "S2" : data["S2"].DF.qHL,

                            })

    timePlot = time[0:len(data["W1"].DF.qHL)]
    toPlot = toPlot.set_index(timePlot)
    toPlot = toPlot.resample("d").sum()
    toPlot = toPlot.resample("w").mean()

    sns.lineplot(data=toPlot, ax = ax)
    
    fig.suptitle('Täglicher Wärmeeintrag im Wochendurchschnitt der einzelnen Gebäude', fontsize=18)
    ax.legend(loc='lower center', ncol = 5)
    ax.set_xlabel('Zeit [Woche]', fontsize=14)
    ax.set_ylabel('Wärmefluss [kWh/d]', fontsize=14)
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
                            "G1" : data["G1"].DF.tInnen,
                            "G2" : data["G2"].DF.tInnen,
                            "G3" : data["G3"].DF.tInnen,
                            "G4" : data["G4"].DF.tInnen,
                            "S1" : data["S1"].DF.tInnen,
                            "S2" : data["S2"].DF.tInnen,
                            })

    timePlot = time[0:len(data["W1"].DF.tInnen)]
    toPlot = toPlot.set_index(timePlot)
    #toPlot = toPlot.resample("d").sum()
    #toPlot = toPlot.resample("w").mean()

    sns.lineplot(data=toPlot, ax = ax)
    
    fig.suptitle('Innentempemperatur der einzelnen Gebäude', fontsize=18)
    ax.legend(loc='upper left', ncol = 2)
    ax.set_xlabel('Zeit [h]', fontsize=14)
    ax.set_ylabel('Innentemperatur [°C]', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

