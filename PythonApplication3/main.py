import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma

layerdict = dict()
layerdict['Xc'] = [50.6, 69.4, 69.4, 50.6, 50.6, 50.2, 69.8, 69.8, 50.2, 50.2, 69.053, 69.12, 69.12]
layerdict['Yc'] = [50.6, 50.6, 69.4, 69.4, 50.6, 50.2, 50.2, 69.8, 69.8, 50.2, 50.88, 50.996, 51.796]

highlightmask = np.ones(len(layerdict['Xc'])).astype(bool)
highlightmask[4:6] = highlightmask[9:11] = False

layerdict['Xc'] = ma.array(layerdict['Xc'])
layerdict['Yc'] = ma.array(layerdict['Yc'], mask=highlightmask)

plt.plot(layerdict['Xc'], layerdict['Yc'].data, label='linepath', linewidth=3.5)
plt.plot(layerdict['Xc'], layerdict['Yc'], 'r', linewidth=3.5)
plt.xlabel('X')
plt.ylabel('Y')
plt.show()