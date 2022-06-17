

from Simulation import Simulation
from PE_CO2 import konversionsfaktoren






for szen in ["FW","WP"]:
	sim = Simulation()
	sim.Simulate(szen)
	sim.GetStrombedarf(szen)
	sim.ExportData(szen)






print(f"Summe Stromverbrauch Wohnen: {sim_WP.summeWohnen} kWh")
print(f"Summe Stromverbrauch Gewerbe: {sim_WP.summeGewerbe} kWh")
print(f"Summe Stromverbrauch Schule: {sim_WP.summeSchule} kWh")
print(f"Summe Stromverbrauch Gesamt: {sum(sim_WP.summeGesamt)} kWh")