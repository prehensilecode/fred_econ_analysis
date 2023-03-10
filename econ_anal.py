#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time

from fredapi import Fred

debug_p = False

plt.style.use('fivethirtyeight')
#pd.set_option('max_columns', 500)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]

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
    time.sleep(0.3) # throttle requests to FRED

unemp_results = pd.concat(all_results, axis=1)

# drop columns whose names are > 4
cols_to_drop = []
for i in unemp_results:
    if debug_p:
        print(i)

    if len(i) > 4:
        cols_to_drop.append(i)

unemp_results = unemp_results.drop(columns=cols_to_drop, axis=1)

unemp_states = unemp_results.copy()
unemp_states.dropna(inplace=True)

id_to_state = unemp_df['title'].str.replace('Unemployment Rate in ', '').to_dict()
unemp_states.columns = [id_to_state[c] for c in unemp_states.columns]

fig = px.line(unemp_states)
fig.write_image('unemp_states.png')

# pull Apr 2020 unemployment rate by state
ax = unemp_states.loc[unemp_states.index == '2020-05-01'].T \
    .sort_values('2020-05-01') \
    .plot(kind='barh', figsize=(8, 12), width=0.8,  edgecolor='black',
          title='Unemployment Rate by State, May 2020')
ax.legend().remove()
ax.set_xlabel('% Unemployed')
plt.savefig('unemployment_2020-05.png', bbox_inches='tight')



# participation rate
part_df = fred.search('participation rate state', filter=('frequency', 'Monthly'))
part_df = part_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')

part_id_to_state = part_df['title'].str.replace('Labor Force Participation Rate for ', '').to_dict()

all_results = []
for myid in part_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
    time.sleep(0.3) # throttle requests to FRED

part_states = pd.concat(all_results, axis=1)
part_states.columns = [part_id_to_state[c] for c in part_states.columns]

# fix DC
unemp_states = unemp_states.rename(columns={'the District of Columbia': 'District of Columbia'})

fig, axs = plt.subplots(10, 5, figsize=(30, 30), sharex=True)
axs = axs.flatten()

i = 0
for state in unemp_states.columns:
    if state in ["District of Columbia", "Puerto Rico"]:
        continue

    ax2 = axs[i].twinx()
    unemp_states.query('index >= 2020 and index < 2022')[state] \
        .plot(ax=axs[i], label='Unemployment')
    part_states.query('index >= 2020 and index < 2022')[state] \
        .plot(ax=ax2, label='Participation', color=color_pal[1])
    ax2.grid(False)
    axs[i].set_title(state)
    i += 1

plt.tight_layout()
plt.savefig('unemp_participation.png', bbox_inches='tight')

state_wanted = 'California'
fig, ax = plt.subplots(figsize=(10, 5), sharex=True)
ax2 = ax.twinx()
unemp_states2 = unemp_states.asfreq('MS')
line1 = unemp_states2.query('index >= 2020 and index < 2022')[state_wanted] \
    .plot(ax=ax, label='Unemployment')
line2 = part_states.dropna().query('index >= 2020 and index < 2022')[state_wanted] \
    .plot(ax=ax2, label='Participation', color=color_pal[1])
ax2.grid(False)
ax.set_title(state_wanted)
fig.legend(labels=['Unemployment', 'Participation'])
plt.savefig('california.png', bbox_inches='tight')


