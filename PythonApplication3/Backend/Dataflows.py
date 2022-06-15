


class Dataflows():


    def __init__(self) -> None:
        self.tInnen = []  #Liste die die Innentemperaturen der Gebäude enthält
        self.qHL = []  #Liste mit den Energieflussen des Gebaudes
        self.qWW = []  #Liste mit dem Warmwasserverbrauch des Gebaudes
        self.stromBedarf = [] #Liste die den Strombedarf aller Nutzer enthalt (Wohnen+Gewerbe)
        self.szen = None
        
        
    def InitSzenWP(self):
        #self.szen = "WP"
        self.stromWP_HZG = [] #Liste mit dem verbrauchten Strom der Warmepumpe fur Heizen
        self.qWP_HZG = []     #Liste mit der erzeugten Wärme der Warmepumpe fur Heizen

        self.stromWP_WW = []  #Liste mit dem verbrauchten Strom der Warmepumpe fur Warmwasser
        self.qWP_WW = []      #Liste mit der erzeugten Wärme der Warmepumpe fur Warmwasser

    def InitSzenFW(self):
        #self.szen = "FW"
        self.stromWP_HZG = [] #Liste mit dem verbrauchten Strom der Warmepumpe fur Heizen
        self.qWP_HZG = []     #Liste mit der erzeugten Wärme der Warmepumpe fur Heizen

