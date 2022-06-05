# -*- coding: cp1252 -*-
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
import bokeh
import pandas as pd
import numpy as np

from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')
time = pd.to_datetime(time)

def PlotStatusCollection(data):
    cars_Charging = []
    cars_Away = []
    fig, ax = plt.subplots()

    
    for subData in data:
        cars_Charging.append(subData.count(True))
        cars_Away.append(subData.count(False))

    toPlot = pd.DataFrame({ "Laden" : cars_Charging,
                            "Fahren" : cars_Away
                            })

    timePlot = time[0:len(cars_Charging)]
    toPlot = toPlot.set_index(timePlot)

    ax.stackplot(toPlot.index,toPlot["Laden"], toPlot["Fahren"],
        labels=['Laden', 'Fahren'],
        colors= ["green", "red"])

    fig.suptitle('Gesammelter Status aller Autos', fontsize=16)
    ax.legend(loc='upper left')
    ax.set_xlabel('Stunde [h]')
    ax.set_ylabel('Anzahl Autos')
    plt.show()

def PlotPersonStatus(data):
    cars_Charging = []
    cars_Away = []
    fig, ax = plt.subplots()


    for subData in data:
        cars_Charging.append(subData.count(True))
        cars_Away.append(subData.count(False))
    
    toPlot = pd.DataFrame({ "Fahrbereit" : cars_Charging,
                            "Unterwegs" : cars_Away
                            })
    timePlot = time[0:len(cars_Charging)]
    toPlot = toPlot.set_index(timePlot)

    print(toPlot.info(verbose = True))

    ax.stackplot(toPlot.index,toPlot["Fahrbereit"], toPlot["Unterwegs"],
        labels=['Fahrbereit', 'Unterwegs'],
        colors= ["green", "red"])

    fig.suptitle('Status der mobilen Personen', fontsize=16)
    ax.legend(loc='upper left')
    ax.set_xlabel('Stunde [h]')
    ax.set_ylabel('Anzahl Personen')
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
        if i == anzCars-1:
            ax[i].set_xlabel("Stunde")
        else:
            ax[i].set_xlabel("")
            ax[i].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
    fig.suptitle('Auszug des Status der Autos', fontsize=20)

    plt.show()

def PlotUseableCapacity(data, resLast):

    time = np.arange('2022-01-01', '2023-01-01', dtype='datetime64[h]')

    fig, ax = plt.subplots(4, figsize=(10,10))
    df = pd.DataFrame(index = time)
    df["Kap"] = data
    df["resLast"] = resLast
    months = ["Januar","Februar","Marz","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    for i,month in enumerate([3,6,9,12]):
        toPlot = df[df.index.month == month]
        toPlot["Kap"].plot(kind = "line", ax = ax[i], color = "black", legend = False)
        ax2 = ax[i].twinx()
        toPlot["resLast"].plot(kind = "line", ax = ax2, color = "red", legend = False)
        ax[i].set_xlabel('')
        ax[i].set_ylabel('Kapazitat [kWh]')
        #ax[i].set_ylim(-100,200)
        ax[i].set_title(months[month-1])
    fig.suptitle('Verwendbare Kapazitat der angeschlossenen Autos', fontsize=16)
    
    plt.show()

def PlotResiduallast(pv, strom, reslast):
    fig, ax = plt.subplots()  

    
    pv = pv[0:len(reslast)]
    strom = strom[0:len(reslast)]

    toPlot = pd.DataFrame({ "PV-Ertrag" : pv,
                            "Stromverbrauch" : strom,
                            "Residuallast" : reslast
                            })

    timePlot = time[0:len(reslast)]
    toPlot = toPlot.set_index(timePlot)
    #toPlot = toPlot.resample("d").sum()

    sns.lineplot(data=toPlot, ax = ax)
    
    fig.suptitle('PV-Ertrag, Stromverbrauch und Residuallast des Quartiers', fontsize=18)
    ax.legend(loc='lower left', fontsize=12)
    ax.set_xlabel('Zeit [h]', fontsize=18)
    ax.set_ylabel('Energie [kWh]', fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='black', linestyle='-', linewidth=0.2)
    plt.show()

def CalcEigenverbrauch(pv, reslast): 
    pv = pv[0:len(reslast)]
    Einspeisung = abs(sum([x for x in reslast if x < 0]))

    Eigenverbrauchsanteil = 1 - Einspeisung/sum(pv)
    Eigenverbrauch = int(sum(pv) * Eigenverbrauchsanteil)
    Überschuss = int(sum(pv) - sum(pv) * Eigenverbrauchsanteil)
    return Eigenverbrauch, Überschuss

def plot_stacked_bar(data, series_labels, category_labels=None, 
                     show_values=False, value_format="{}", y_label=None, 
                     colors=None, grid=True, reverse=False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will 
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    colors          -- List of color labels
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis=1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        color = colors[i] if colors is not None else None
        axes.append(plt.bar(ind, row_data, bottom=cum_size, 
                            label=series_labels[i], color=color))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend()

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                plt.text(bar.get_x() + w/2, bar.get_y() + h/2, 
                         value_format.format(h), ha="center", 
                         va="center")

def PlotEigenverbrauchmitAutoeinspeisung(pv, reslast, resLastAfterCharging):
    fig, ax = plt.subplots()  

    
    
    Eigenverbrauch, Überschuss = CalcEigenverbrauch(pv,reslast)
    newResLast = [x + y for (x, y) in zip(reslast, resLastAfterCharging)]

    print(f"Summe alte ResLast: {sum(reslast)}")
    print(f"Summe neue ResLast: {sum(newResLast)}")
    print(f"Differenz: {sum(reslast) - sum(newResLast)}")

    EigenverbrauchAfterCharging, ÜberschussAfterCharging = CalcEigenverbrauch(pv,newResLast)

    print(Eigenverbrauch)
    print(Überschuss)
    print(EigenverbrauchAfterCharging)
    print(ÜberschussAfterCharging)

    plot_stacked_bar(data= [[Eigenverbrauch,Überschuss],[EigenverbrauchAfterCharging, ÜberschussAfterCharging]],
                     series_labels=["1","2","3","4"])

    labels = ['Standard', 'mit E-Mobilität',]
    Eigenverbrauchplot = [Eigenverbrauch, EigenverbrauchAfterCharging]
    Überschuss = [Überschuss, ÜberschussAfterCharging]
    width = 0.35       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    ax.bar(labels, Eigenverbrauchplot, width, label='Eigenverbrauch')
    ax.bar(labels, Überschuss, width, bottom=Eigenverbrauchplot,
           label='Einspeisung')

    ax.set_ylabel('kWh')
    ax.set_title('Einspeisung zu Autoladung')
    ax.legend()
   
    plt.show()

def PlotEigenverbrauch(pv, reslast):
    fig, ax = plt.subplots()  

    Eigenverbrauch,Überschuss = CalcEigenverbrauch(pv,reslast)

    labels = ["Überschuss", "Eigenverbrauch"]
    sizes = [Eigenverbrauch, Überschuss]
    
    fig.suptitle('Eigenverbrauchsanteil am PV-Ertrag des Quartiers', fontsize=18)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.show()


def PlotSOC(data, anzAuto):
    #Daten Aufbereitung    
        
    def PickData(schritt, anzAuto):
        istSOC = []
        sollSOC = []
        correctionSoll = []
        correctionIst = []

        schrittSoll = sorted(schritt, key=lambda x: x.minLadung, reverse=True)
        schrittIst = sorted(schritt, key=lambda x: x.kapazitat, reverse=True)

        for car in schrittSoll: #anzAutos
            sollSOC.append(car.minLadung * car.maxLadung)
        
        for car in schrittIst: #anzAutos
            istSOC.append(car.kapazitat)

        xWhite = np.linspace(len(istSOC),anzAuto,anzAuto-len(istSOC))        
        for _ in range(len(istSOC),anzAuto):
            correctionIst.append(istSOC[-1])
            correctionSoll.append(sollSOC[-1])
            istSOC.append(istSOC[-1])
            sollSOC.append(sollSOC[-1])

        return istSOC, sollSOC, xWhite, correctionSoll, correctionIst


    x = np.linspace(0,anzAuto,anzAuto)
    fig, ax = plt.subplots()

    fps = 4.8
    duration = (1 / fps) * len(data)
    def make_frame(t):

        ax.clear()
        index = int(t / (1 / fps))
        istSOC, sollSOC, xWhite, correctionSoll, correctionIst = PickData(data[index], anzAuto)
        # plotting line    
        
        ax.plot(x, sollSOC, color= "#038222")
        ax.plot(xWhite, correctionSoll, color= "white", lw=10)

        ax.plot(x, istSOC, color= "#9e0303")
        ax.plot(xWhite, correctionIst, color= "white", lw=10)

        ax.set_ylim(0, 80)
     
        # returning numpy image
        return mplfig_to_npimage(fig)

    # creating animation
    animation = VideoClip(make_frame, duration = duration)
 
    # displaying animation with auto play and looping
    animation.ipython_display(fps = fps, loop = True, autoplay = True)