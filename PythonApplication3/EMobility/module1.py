liAutos = [0,1,1,1,1,1,1,2,3,4,5,6,7,8,9]
def PickCar(demand):
    safety = 1
    demand = demand * safety

    if liAutos[-1] < demand:
        return False

    index = next(x[0] for x in enumerate(liAutos) if x[1] >= demand)
    print(f"Best Choice: {index}")
    return index

PickCar(8.5)
