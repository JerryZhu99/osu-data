import os
import sys


import numpy as np
import pandas as pd

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl

import local_data

beatmap_data = local_data.get_beatmaps(sys.argv[1])
beatmaps = pd.DataFrame(beatmap_data).dropna().to_dict('list')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(beatmaps["ApproachRate"],
                beatmaps["HPDrainRate"],
                beatmaps["OverallDifficulty"], c=beatmaps["CircleSize"])

ax.set_xlabel('ApproachRate')
ax.set_ylabel('HPDrainRate')
ax.set_zlabel('OverallDifficulty')

cbar = plt.colorbar(sc)
cbar.ax.set_ylabel('CircleSize')

plt.show()
