
class cla_PV_Anlage():
    def __init__(self, var_PV_kWp,var_PV_EK):
        self.PV = var_PV_kWp #kW
        self.PV_EK = self.PV * var_PV_EK / 1000 #kW


class cla_Gebaude():
    def __init__(self, var_BGF, var_EV):
        self.BGF = var_BGF   #m²
        self.EV = var_EV * self.BGF / 1000   #kW

