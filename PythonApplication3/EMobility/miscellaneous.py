# -*- coding: <latin-1> -*-

import numpy as np
import pandas as pd
from random import seed, randint
from math import radians, cos, sin, sqrt
seed(10)

class Person():

	def __init__(self):
		self.status = True #Status der Person True = Anwesend, False = Unterwegs
		self.x = 0
		self.y = 0
		self.anzAutoWege = 0
		self.wegGesamt = 0
		self.wegMitAuto = 0
		self.carID = None
		self.borrowTime = 0 #gibt an wie lange das Auto bereits ausgeborgt worden ist
		self.waitingTime = 0 #gibt an wie lange die Person bereits wartet zu fahren

	def AddWay(self, distance):
		alpha = radians(randint(0,359)) #alpha beschreibt die zufallige Richtung in die wir uns bewegen konnen in Bogenmas
		distance = self.RoadtoAirDistance(distance)

		self.x = cos(alpha) * distance + self.x
		self.y = sin(alpha) * distance + self.y

	def WaybackHome(self):
		"""Berechnet den nachhauseweg in km"""
		return self.AirtoRoadDistance(sqrt(self.x**2 + self.y**2))

	def RoadtoAirDistance(self,distance):
		"""Nimmt eine bewegte Strecke und wandelt diese in eine Luftliniendistanz um"""
		return distance / 1.417
	def AirtoRoadDistance(self,distance):
		"""Nimmt eine bewegte Strecke und wandelt diese in eine Luftliniendistanz um"""
		return distance * 1.417
