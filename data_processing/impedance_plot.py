#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
font= {'family': 'Arial',
        'size': 7}
mpl.rc('font', **font)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as md
import numpy as np
from pytz import timezone
import pandas as pd
from glob import glob
import arrow
import os
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

directories = ['mud', 'tap_attempt2']
for d in directories:
    avgdata = [];
    if not os.path.exists("soil_data.pkl"):
        fnames = glob("data/" + d + "/soil*.csv")
        #fnames = glob("data/tap_attempt2/soil*.csv")
        soil_data = None

        for fname in sorted(fnames, key=lambda x: int(x.split('.')[0].split('_')[-1])):
            print(fname)
            data = np.genfromtxt(fname, dtype=float, delimiter=',',skip_header=11)
            data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current':np.abs(data[:,3]*10E-12), 'voltage':np.abs(data[:,4]*10E-9)})
            data.timestamp = data.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
            data['power'] = np.abs(np.multiply(data['current'], data['voltage']))
            avgdata.append({'mcurrent':np.mean(data['current']), 'mvoltage':np.mean(data['voltage']),'mpower':np.mean(data['power'])})
            data.set_index('timestamp', inplace=True)
            #print(data)
            if soil_data is None:
                soil_data = data
            else:
                soil_data = pd.concat([soil_data, data])
        #soil_data.to_pickle("soil_data.pkl");
    else:
        soil_data = pd.read_pickle("soil_data.pkl")
    #mv = soil_data.rolling(5*60).mean()
    avgdata = pd.DataFrame(avgdata)
    print(avgdata)

    plt.close()
    plt.xlabel("impedance (ohms)")
    fig, (ax1, ax3) = plt.subplots(2,figsize=(4,2), sharex=True)
    #fig.autofmt_xdate()

    volt_color= 'tab:blue'
    amp_color = 'tab:red'
    ax1.set_ylabel('Cell Voltage (V)')
    ax1.plot(avgdata.index, avgdata['mvoltage'], color=volt_color)
    ax1.tick_params(axis='y', labelcolor=volt_color)
    ax1.set_ylim(0, 1.1)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Harvesting Current (μA)')
    ax2.plot(avgdata.index, 1E6*avgdata['mcurrent'], color=amp_color)
    ax2.tick_params(axis='y', labelcolor=amp_color)
    ax2.set_ylim(0,1100)

    ax1.tick_params(axis='x', which='both', length=0)
    ax2.tick_params(axis='x', which='both', length=0)

    ax1.grid(True)

    #ax3.fmt_xdata = md.DateFormatter('%s')
    ax3.set_ylabel("Power (uW)")
    ax3.grid(True)
    ax3.set_ylim(0, 270)
    ax3.plot(avgdata.index, 1E6*avgdata['mpower'])
    plt.xticks(np.arange(11), ['68', '100', '1k', '2k','3.3k','4.7k','6.8k','9.1k','15k','39k','82k'])

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.5)
    plt.subplots_adjust(hspace=0.15)
    #plt.savefig('farm_experiment.pdf')
    plt.savefig(d + '_impedance.pdf')
    plt.close()
    tot_energy = np.trapz(soil_data['power'])
    print(tot_energy)
    print((soil_data.tail(1).index - soil_data.head(1).index).total_seconds())

