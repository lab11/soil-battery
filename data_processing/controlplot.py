#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
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
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

if not os.path.exists("soil_data.pkl"):
    fnames = glob("data/labincubate/rocket3/soil*.csv")
    soil_data = None

    for fname in sorted(fnames, key=lambda x: int(x.split('.')[0].split('_')[-1])):
        print(fname)
        data = np.genfromtxt(fname, dtype=float, delimiter=',',skip_header=11)
        data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current1':np.abs(data[:,4]*10E-12), 'voltage1':np.abs(data[:,5]*10E-9), 'current2':np.abs(data[:,8]*10E-12), 'voltage2':np.abs(data[:,6]*10E-9)})
        data.timestamp = data.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        data['power1'] = np.abs(np.multiply(data['current1'], data['voltage1']))
        data['power2'] = np.abs(np.multiply(data['current2'], data['voltage2']))
        data.set_index('timestamp', inplace=True)
        print(data)
        if soil_data is None:
            soil_data = data
        else:
            soil_data = pd.concat([soil_data, data])

    print(soil_data)
    #soil_data.to_pickle("soil_data.pkl");
else:
    soil_data = pd.read_pickle("soil_data.pkl")
    print(soil_data)

mv = soil_data.rolling(5*60).mean()

plt.close()
plt.xlabel("Time")
fig, (ax1, ax3) = plt.subplots(2,figsize=(4,2), sharex=True)
fig.autofmt_xdate()


volt_color= 'tab:blue'

amp_color = 'tab:red'


volt_color1= 'tab:blue'
volt_style1 = 'dashed'
volt_color2= 'tab:green'
volt_style2 = 'dotted'
amp_color1 = 'tab:red'
amp_style1='dashed'
amp_color2 = 'tab:orange'
amp_style2='dashdot'
ax1.set_ylabel('Cell Voltage (V)')
ax1.plot(mv.index, mv['voltage1'], color=volt_color1, ls=volt_style1)
#ax1.plot(mv.index, mv['voltage2'], color=volt_color2, ls=volt_style2)
ax1.tick_params(axis='y', labelcolor=volt_color1)
ax1.set_ylim(0, 0.35)

ax2 = ax1.twinx()
ax2.set_ylabel('Harvesting Current (μA)')
ax2.plot(mv.index, 1E6*mv['current1'], color=amp_color1, ls=amp_style1)
#ax2.plot(mv.index, 1E6*mv['current2'], color=amp_color2, ls=amp_style2)
ax2.tick_params(axis='y', labelcolor=amp_color1)
ax2.set_ylim(0,250)
ax1.tick_params(axis='x', which='both', length=0)
ax2.tick_params(axis='x', which='both', length=0)

ax1.grid(True)
ax1.legend(['volts','Cu volts'], loc='upper left', prop={'size': 6})
ax2.legend(['amps','Cu amps'], loc='upper right' , prop={'size': 6})

#ax3.fmt_xdata = md.DateFormatter('%m-%d')
ax3.xaxis.set_major_formatter(md.DateFormatter('%m-%d'))
ax3.set_ylabel("Power (uW)")
ax3.grid(True)
print('max power: ',max(max(1E6*data['power1']),max(1E6*data['power2'])))
ax3.set_ylim(0,35)
ax3.plot(mv.index, 1E6*mv['power1'], color=volt_color1, ls = volt_style1)
#ax3.plot(mv.index, 1E6*mv['power2'], color=volt_color2, ls = volt_style2)
#ax3.legend(['C','Cu'], loc='upper right', prop={'size': 6})
ax3.tick_params(axis='x', labelsize=6, rotation=0)
#ax3.set_xlim(mv.index[0], datetime.date(2020,5,19))
for label in ax3.get_xticklabels():
    label.set_horizontalalignment('center')

plt.tight_layout(pad=0.6, w_pad=0.5, h_pad=0.6)
plt.subplots_adjust(hspace=0.15)
plt.savefig('control.pdf')
plt.close()
tot_energy = np.trapz(soil_data['power1'])
tot_energy = np.trapz(soil_data['power2'])
print(tot_energy)
print((soil_data.tail(1).index - soil_data.head(1).index).total_seconds())

