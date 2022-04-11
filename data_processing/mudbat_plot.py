#!/usr/bin/env python3
import matplotlib as mpl
#mpl.use('Agg')
font= {'family': 'Arial',
        'size': 7}
mpl.rc('font', **font)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as md
import datetime
import numpy as np
from pytz import timezone
import pandas as pd
from glob import glob
import arrow
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

if not os.path.exists("mudbat_data.pkl"):
    fnames = glob("data/carbon-carbon/mudbat*.csv")
    mudbat_data = None

    for fname in sorted(fnames, key=lambda x: int(x.split('.')[0].split('_')[-1])):
        data = np.genfromtxt(fname, dtype=float, delimiter=',',skip_header=11)
        if '3' in fname:
            data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current':data[:,3]*-10E-12, 'voltage':data[:,4]*-10E-9})
        else:
            data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current':data[:,3]*10E-12, 'voltage':data[:,4]*10E-9})
        data.timestamp = data.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        if '3' in fname:
            start = data['timestamp'][0]
        data['power'] = np.abs(np.multiply(data['current'], data['voltage']))
        if mudbat_data is None:
            mudbat_data = data
        else:
            mudbat_data = pd.concat([mudbat_data, data])

    #mudbat_data.to_pickle("mudbat_data.pkl");
else:
    mudbat_data = pd.read_pickle("mudbat_data.pkl")

mudbat_data.iloc[:, 1:4] = mudbat_data.iloc[:, 1:4].rolling(5*60).mean()

ind = mudbat_data['timestamp'] > start
mudbat_data = mudbat_data[ind]


def mudbat_plot():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            specs=[[{"secondary_y": True}], [{"secondary_y":False}]],
                            )

        fig.add_trace(
                go.Scatter(x=mudbat_data['timestamp'], y=mudbat_data['voltage'], mode='lines', name='voltage'),
                row=1, col=1,
                secondary_y=False
        )
        fig.add_trace(
                go.Scatter(x=mudbat_data['timestamp'], y=mudbat_data['current'], mode='lines', name='current'),
                row=1, col=1,
                secondary_y=True
        )
        fig.add_trace(
                go.Scatter(x=mudbat_data['timestamp'], y=mudbat_data['power'], mode='lines', showlegend=False),
                row=2, col=1
        )

        fig.update_xaxes(title={'text':"Impedance (Ω)"}, row=2, col=1)
        fig.update_yaxes(title={'text':"Cell Voltage (mV)", 'standoff':5}, row=1,col=1, secondary_y=False)
        fig.update_yaxes(title={'text':"Harvesting Current (μA)"}, row=1,col=1, secondary_y=True)
        fig.update_yaxes(title={'text':"Power (uW)", 'standoff':5}, row=2, col=1)
        fig.update_layout(height=500, width=700, title="Mudbat Subplots",template='plotly_dark', 
                          paper_bgcolor="#121212", plot_bgcolor="#121212",
                          legend={'orientation':'h', 'xanchor':'right', 'yanchor': 'bottom', 'y':1.02, 'x':1}
                          )
        
        return fig