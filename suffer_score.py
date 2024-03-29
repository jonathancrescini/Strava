import pandas as pd
import datetime as dt
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import dash
import dash_core_components as dcc
import dash_html_components as html

pio.renderers.default = 'browser'

activities = pd.read_csv('activities.csv')
activities['start_date'] = pd.to_datetime(activities['start_date'])
activities.index = activities['start_date'].dt.date
activities['weekNum'] = activities.start_date.dt.week
activities['year'] = activities.start_date.dt.year

all_cols = activities.columns
cols = ['name', 'type', 'suffer_score', 'weekNum', 'year', 'start_date']
activities = activities[cols]


firstDay = min(activities.index)
''' extract suffer_score and group by day to take into account days
with multiple activities
'''

suffer_score = activities['suffer_score'].groupby(by=activities.index).sum()

# Create calendar
calendar = []
today = dt.date.today()
n = (today - firstDay).days

for i in range(n+1):
    calendar.append(today + dt.timedelta(days=-i))

del i

# Create Main dataframe from which will be calculated suffer score
df = pd.DataFrame(index=calendar,
                  columns=['date', 'year', 'month', 'week',
                           'dailySuffer', 'Last7DaysSuffer'])
df['date'] = calendar
df['date'] = pd.to_datetime(df['date'])
df['year'] = df.date.dt.year
df['month'] = df.date.dt.month
df['week'] = df.date.dt.week
df['weekday'] = df.date.dt.weekday
df['dailySuffer'] = df.join(suffer_score, how='left')['suffer_score'] \
                    .replace(np.nan, 0)
df.sort_index(ascending=True, inplace=True)

# calculate rolling suffer score (7 days)
df['Last7DaysSuffer'] = df.dailySuffer.rolling(7, min_periods=0).sum()
df['psc1'] = df['Last7DaysSuffer'].shift(7)
df['psc2'] = df['Last7DaysSuffer'].shift(14)
df['psc3'] = df['Last7DaysSuffer'].shift(21)
df['psc4'] = df['Last7DaysSuffer'].shift(28)


''' calculate max recommended suffer score

'''


def recommended_suffer(sc, maxSufferPrev):

    midSuffer = np.mean(sc[1:])

    '''if increasing workload then calculate increase to a max of 10%
    from previous max or 10 suffer points.
    '''

    if sc[0] > midSuffer:
        maxSuffer = max(maxSufferPrev*1.1, maxSufferPrev + 10, 10)
    else:
        maxSuffer = max(min(maxSufferPrev, midSuffer), 10)

    minSuffer = max(maxSuffer - 2*max(maxSuffer-midSuffer, 20), 0)

    return minSuffer, midSuffer, maxSuffer

# initialize max Suffer


minSuffer = []
midSuffer = []
maxSuffer = []

minS = 0
midS = 0
maxS = 0
weekday = today.weekday()
for i, row in df.iterrows():
    if row['weekday'] == weekday:
        minS, midS, maxS = recommended_suffer(
            row[['Last7DaysSuffer', 'psc1', 'psc2', 'psc3', 'psc4']], maxS)

    minSuffer.append(minS)
    midSuffer.append(midS)
    maxSuffer.append(maxS)


df['maxSuffer'] = maxSuffer
df['maxSuffer'] = df.maxSuffer.shift()
df['minSuffer'] = minSuffer
df['minSuffer'] = df['minSuffer'].shift()
df['midSuffer'] = midSuffer


# plot 7 Days suffer score
minDatePlot = today + dt.timedelta(days=-140)

plotData = df.query('weekday ==  @weekday and date >= @minDatePlot')[
    ['Last7DaysSuffer', 'maxSuffer', 'minSuffer', 'midSuffer']]

# create next week min and max recommended suffer
nextWeek = today + dt.timedelta(days=7)
newRow = pd.DataFrame([[np.nan, maxSuffer[-1], minSuffer[-1], midSuffer[-1]]],
                      index=[nextWeek], columns=plotData.columns)
plotData = plotData.append(newRow)


plotSufferArea = plotData['maxSuffer'].append(plotData['minSuffer'][::-1])

fig = go.Figure()
# weekly suffer score
fig.add_trace(go.Scatter(x=plotData.index, y=plotData.Last7DaysSuffer,
                         mode='markers', name='Suffer score'))

# area of recommended suffer
fig.add_trace(go.Scatter(x=plotSufferArea.index, y=plotSufferArea.values,
                         fill='toself', fillcolor='rgba(0,100,80,0.2)',
                         line_color='rgba(255,255,255,0)',
                         name='Best range', mode='markers'))


fig.add_trace(go.Scatter(x=plotData.index, y=plotData.midSuffer, mode='lines',
                         name='4W AVG Suffer', line_shape='spline'))

# fig.update_layout(hovermode='x unified')

fig.show()


data = activities.query('year==2021 and weekNum == 50')[
    ['name', 'type', 'suffer_score']].reset_index()
table = go.Figure(data=[go.Table(
    header=dict(values=data.columns),
    cells=dict(values=data.transpose()))
    ])
table.show()


# %%


app = dash.Dash()
app.layout = html.Div([
    html.Div([dcc.Graph(figure=fig)]),
    html.Div([dcc.Graph(figure=table)])
])

app.run_server(debug=False, use_reloader=False)
# Turn off reloader if inside Jupyter
