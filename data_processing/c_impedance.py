#!/usr/bin/env python3

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

avgdata = {
        'mcurrent':[2.2, 3.2, 12.3, 14.8, 16.3, 17.1, 17.7, 18, 19, 20, 20],
        'mvoltage':[1.38, 1.92, 15.7, 26.7, 39.3, 48, 58.7, 70, 86, 120, 176],
        'mpower':[0.003, 0.006, 0.19, 0.4, 0.64, 0.82, 0.84, 1.06, 1.33, 2.4, 3.52],
        'impedance':[68, 100, 1e3, 2e3, 3.3e3, 4.7e3, 6.8e3, 9.1e3, 15e3, 39e3, 82e3]
        }
avgdata = pd.DataFrame(avgdata)

def c_impedance_plot():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            specs=[[{"secondary_y": True}], [{"secondary_y":False}]]
                            )

        fig.add_trace(
                go.Scatter(x=avgdata['impedance'], y=avgdata['mvoltage'], mode='lines', name='voltage'),
                row=1, col=1,
                secondary_y=False
        )
        fig.add_trace(
                go.Scatter(x=avgdata['impedance'], y=avgdata['mcurrent'], mode='lines', name='current'),
                row=1, col=1,
                secondary_y=True
        )
        fig.add_trace(
                go.Scatter(x=avgdata['impedance'], y=avgdata['mpower'], mode='lines', showlegend=False),
                row=2, col=1
        )

        fig.update_xaxes(title={'text':"Impedance (Ω)"}, row=2, col=1)
        fig.update_yaxes(title={'text':"Cell Voltage (mV)", 'standoff':5}, row=1,col=1, secondary_y=False)
        fig.update_yaxes(title={'text':"Harvesting Current (μA)"}, row=1,col=1, secondary_y=True)
        fig.update_yaxes(title={'text':"Power (uW)", 'standoff':20}, row=2, col=1)
        fig.update_layout(height=500, width=700, title="Impedance Subplots",template='plotly_dark', 
                          paper_bgcolor="#121212", plot_bgcolor="#121212"
                          )
        
        return fig