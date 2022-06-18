
from numpy.random import default_rng, Generator, PCG64
import numpy as np
rng = Generator(PCG64(10))

mean = 4
std = 1

std = std/3

for i in range(100):
    val = rng.normal(loc= mean, scale= std, size= 1)

    if mean - val < 1*std:
        print(val)
    else:
        print("Nochmal")
