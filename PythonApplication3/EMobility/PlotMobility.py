
import seaborn as sns
import matplotlib.pyplot as plt
import bokeh
import pandas as pd
def PlotStatusCollection(data):
    cars_Charging = []
    cars_Away = []

    for subData in data:
        cars_Charging.append(subData.count(True))
        cars_Away.append(subData.count(False))

    toPlot = pd.DataFrame({ "Laden" : cars_Charging,
                            "Fahren" : cars_Away
                            })
    hours = list(range(len(cars_Charging)))

    sns.set_theme()
    plt.stackplot(hours,toPlot["Laden"], toPlot["Fahren"],
        labels=['Laden', 'Fahren'],
        colors= ["green", "red"])

    plt.legend(loc='upper left')
    plt.xlabel('Stunde')
    plt.ylabel('Autos')
    plt.show()

def PlotSample(data, anzCars, hours):
    subData = []
    toPlot = pd.DataFrame()
    fig, ax = plt.subplots(anzCars)
    for i in range(anzCars):
        carlist = []
        for k in range(hours):
            carlist.append(data[k][i])
        toPlot[str(i)] = carlist
        toPlot[str(i)] = toPlot[str(i)].astype(int)
        toPlot[str(i)].plot(kind = "line", ax = ax[i], color = "black")


    plt.show()