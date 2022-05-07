

import seaborn as sns
import matplotlib.pyplot as plt
import bokeh
import pandas as pd

class DataScraper():

    def __init__(self) -> None:
        self.Init_eMobility()
        

    def Init_eMobility(self):
        self.li_state = []			#Liste in denen der Status der Autos gesammelt wird (Wird spater geplottet)
        self.useableCapacity = []	#Liste in der die verwendbare Kapazitat gespeichert wird zum plotten
        self.demand = []			#Liste in der der Bedarf von Au�erhalb gespeichert wird
        self.demandDriving = []		#Liste in der der Bedarf der Autos zum Fahren gespeichert wird
        self.demandcovered = []		#Liste in der der Bedarf der durch die E-Autos gedeckt wird gespeichert wird
        self.generation = []		#Liste in der die von au�erhalb produzierte Leistung gespeichert wird
        self.generationloaded = []  #Liste die speichert, wie viel Energie in den Autos gespeichert wurde
        self.resLast = []           #Liste in der die Residuallast gespeichert wird
                


Scraper = DataScraper()