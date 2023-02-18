#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time

from fredapi import Fred

plt.style.use('fivethirtyeight')
#pd.set_option('max_columns', 500)
#color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]

def read_api_key(filename):
    with open(filename, 'r') as f:
        return f.read().strip()


fred_key = read_api_key('fred_key.txt')

# Fred object
fred = Fred(api_key=fred_key)

# Search econ. data
sp_search = fred.search('S&P', order_by='popularity')

print(sp_search.head())

# pull raw data and plot
sp500 = fred.get_series(series_id='SP500')
sp500.plot(figsize=(10,5), title='S&P 500', lw=2)
plt.savefig('sp500.png')

# pull and join multiple series
unemp_df = fred.search('unemployment rate state', filter=('frequency', 'Monthly'))
unemp_df = unemp_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')
unemp_df = unemp_df.loc[unemp_df['title'].str.contains('Unemployment Rate')]

all_results = []

for myid in unemp_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
    time.sleep(0.1) # throttle requests to FRED

unemp_results = pd.concat(all_results, axis=1)

cols_to_drop = []
for i in unemp_results:
    if len(i) > 4:
        cols_to_drop.append(i)
unemp_results = unemp_results.drop(columns=cols_to_drop, axis=1)

unemp_states = unemp_results.copy()
unemp_states.dropna(inplace=True)

id_to_state = unemp_df['title'].str.replace('Unemployment Rate in ', '').to_dict()
unemp_states.columns = [id_to_state[c] for c in unemp_states.columns]

fig = px.line(unemp_states)
fig.write_image('unemp_states.png')

