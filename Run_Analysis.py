# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 11:29:32 2021

@author: jonat
"""

import pandas as pd
import numpy as np
import random
import polyline
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot
import datetime as dt

runs = pd.read_csv('runs.csv')
print(runs.head())

# decode and plot polyline
polylines = runs['map.summary_polyline']

ind = random.randrange(0,100,1)
pl = [x for x,y in polyline.decode(polylines[ind])],[y for x,y in polyline.decode(polylines[ind])]
df = pd.DataFrame(pl).T
fig = px.line_mapbox(df, lat=0, lon=1, zoom=3, height=300, width=300)

'''
"carto-positron"
"stamen-toner"
'''
fig.update_layout(mapbox_style="carto-positron" , mapbox_zoom=12, mapbox_center_lat = np.mean(df[0]),
    margin={"r":0,"t":0,"l":0,"b":0})

plot(fig)

fig, ax = plt.subplots()

runs['year'] = pd.to_datetime(runs['start_date']).dt.year
runs['month'] = pd.to_datetime(runs['start_date']).dt.month

runs['average_gradient'] = runs['total_elevation_gain']/runs['distance']
runs['grad_bins'] = pd.cut(runs['average_gradient'], [0,0.02,0.04,0.06, 0.08, 0.1, 0.2], labels=[1,2,3,4,5,6])
x = runs.query('workout_type != 1').groupby(by=['year', 'grad_bins']).average_speed.mean().reset_index()
scatter = ax.scatter(x['grad_bins'], x['average_speed'], c=x['year'], alpha=0.5)

legend1 = ax.legend(*scatter.legend_elements(),
                    loc="upper right", title="Classes")
ax.add_artist(legend1)
plt.show()


#%% HR trends



fig = px.histogram(runs, x='average_heartrate', color='year')
plot(fig)













