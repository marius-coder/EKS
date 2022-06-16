

from Simulation import Simulation





sim_WP = Simulation()


sim_WP.Simulate("FW")
sim_WP.GetStrombedarf()
sim_WP.ExportData()

print(f"Summe Stromverbrauch Wohnen: {sim_WP.summeWohnen} kWh")
print(f"Summe Stromverbrauch Gewerbe: {sim_WP.summeGewerbe} kWh")
print(f"Summe Stromverbrauch Schule: {sim_WP.summeSchule} kWh")
print(f"Summe Stromverbrauch Gesamt: {sum(sim_WP.summeGesamt)} kWh")