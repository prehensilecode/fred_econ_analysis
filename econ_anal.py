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

sp_search.head()
