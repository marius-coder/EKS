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
    carsFahren = []
    carsVollgeladen = []
    carsLadenNichtBereit = []
    carsLadenBereit = []
    fig, ax = plt.subplots()

    
    for subData in data:
        carsFahren.append(subData.count("Fahren"))
        carsVollgeladen.append(subData.count("Vollgeladen"))
        carsLadenNichtBereit.append(subData.count("Laden und nicht bereit"))
        carsLadenBereit.append(subData.count("Laden und bereit"))

    toPlot = pd.DataFrame({ "Fahren" : carsFahren,
                            "Vollgeladen" : carsVollgeladen,
                            "Laden und nicht bereit" : carsLadenNichtBereit,
                            "Laden und bereit" : carsLadenBereit
                            })

    timePlot = time[0:len(carsVollgeladen)]
    toPlot = toPlot.set_index(timePlot)

    ax.stackplot(toPlot.index, toPlot["Fahren"], toPlot["Laden und nicht bereit"], toPlot["Laden und bereit"],toPlot["Vollgeladen"],
        labels=['Fahren','Laden und Mindestladung nicht erreicht', 'Laden und Mindestladung erreicht','Vollgeladen'],
        colors= [ "red", "blue", "orange", "green"])

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


def PlotLadegang(data):
    sns.set_theme(style="whitegrid")
    df = pd.DataFrame()
    df["data"] = data
    df = df.set_index(pd.to_datetime(time))


    maxY = max(df["data"])
    li_Wochentage = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    labelsTage = ["Werktag", "Samstag", "Sonntag"]

    #Lastgang aufgeteilt nach Quartalen
    for quart in range(1,5):            
        liDays = [[],[],[]] 
        for day in range(7):
            liHours = []
            for hour in range(24):      
                df_inter=df[df.index.quarter == quart]
                df_inter=df_inter[df_inter.index.dayofweek == day]["data"]
                df_inter=df_inter[df_inter.index.hour == hour]
                liHours.append(df_inter)
            if day == 5:
                liDays[1].extend(liHours)
            if day == 6:
                liDays[2].extend(liHours)
            else:
                liDays[0].extend(liHours)
        
        fig, ax = plt.subplots(1,3)
        fig.suptitle("Lastgang an verschiedenen Tagen im Quartal: "+str(quart), fontsize = 30)
        for l in range(3):
            sns.boxplot(data=liDays[l], ax = ax[l])   
            ax[l].set_ylim(0,maxY)
            ax[l].set_xlabel("Stunde", fontsize = 15)
            ax[l].set_ylabel("Last [kW]", fontsize = 15)      
            ax[l].set_title("Lastgang am Tag: " + labelsTage[l], fontsize = 20)
        plt.tight_layout()
        plt.show()
        fig.savefig("Lastgang Quartal_"+str(quart)+".png") 

def PlotVerteilungen(data, name):
    fig, ax = plt.subplots()
    hours = np.linspace(0,8759,8760)

    toPlot = pd.DataFrame({ 
                            name : data                            
                            })
    toPlot["Stunde"] = [int(hour % 24) for hour in hours]
    sns.set_theme(style="white")

    sns.boxplot(x="Stunde",y= name, palette="muted", data=toPlot, ax= ax)
    ax.set_title(f"Tagesverteilung: {name} der E-Mobilität")
    ax.set_ylabel("Leistung [kW]")
    ax.yaxis.grid(True)
    plt.show()

def PlotEinflussLDC(Verbrauch, PV, Endladung, Ladung):
    fig, ax = plt.subplots()
    hours = np.linspace(0,8759,8760)
    toPlot = pd.DataFrame({ 
                            "Gebäudeverbrauch" : Verbrauch,
                            "Gebäudeverbrauch mit PV" : [a-b for a,b in zip(Verbrauch,PV)],
                            "Gebäudeverbrauch mit PV/LC" : [a-b-c+d for a,b,c,d in zip(Verbrauch,PV,Endladung,Ladung)]
                            })
    toPlot["Stunde"] = [int(hour % 24) for hour in hours]

    toPlot = toPlot.set_index(pd.to_datetime(time))
    for quart in [3,3]:
        df_inter=toPlot[toPlot.index.quarter == quart]
        #df_inter=toPlot[toPlot.index.month == 8]
        #df_inter=df_inter[df_inter.index.day == 1]
        sns.lineplot(x="Stunde",y= "Gebäudeverbrauch", data=df_inter, ax= ax, color= "blue")
        sns.lineplot(x="Stunde",y= "Gebäudeverbrauch mit PV", data=df_inter, ax= ax, color= "orange")
        sns.lineplot(x="Stunde",y= "Gebäudeverbrauch mit PV/LC", data=df_inter, ax= ax, color= "green")
        ax.set_title("Einfluss des Ladecontrollers auf den stündlichen Gebäudebedarf im Sommer")
        ax.set_ylabel("Verbrauch [kWh]")
        ax.set_xlabel("Stunde")  
        leg = ax.legend(labels = ['Gebäudeverbrauch', 'Gebäudeverbrauch mit PV', 'Gebäudeverbrauch mit PV/LC'], prop={'size': 7},                  
               ncol = 3,facecolor='#f5f5f5', framealpha=1, loc= "lower center")
        for legobj in leg.legendHandles:
            legobj.set_linewidth(5)
        leg.legendHandles[0].set_color('blue')
        leg.legendHandles[1].set_color('orange')
        leg.legendHandles[2].set_color('green')
        #plt.gca().set_ylim(bottom=0)
        ax.yaxis.grid(True) 
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
        
        ax.plot(x, sollSOC, color= "#038222", label= "Mindestladestand")
        ax.plot(xWhite, correctionSoll, color= "white", lw=10)

        ax.plot(x, istSOC, color= "#9e0303", label= "Istladestand")
        ax.plot(xWhite, correctionIst, color= "white", lw=10)
        ax.set_title(f"Ladestand im Vergleich zum Mindestladestand am: {time[int(t)]}")
        ax.set_ylabel("Ladestand [kWh]")
        ax.set_xlabel("Anwesende Autos")
        #print(f"legend handles: {ax.get_legend_handles_labels()}")
        ax.legend()
        
        ax.set_ylim(0, 50)
     
        # returning numpy image
        return mplfig_to_npimage(fig)

    # creating animation
    animation = VideoClip(make_frame, duration = duration)
 
    # displaying animation with auto play and looping
    animation.ipython_display(fps = fps, loop = True, autoplay = True, maxduration= 1000000)