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


avgdata = [];
avgdata.append({'mcurrent':2.2,'mvoltage':1.38,'mpower':0.003})
avgdata.append({'mcurrent':3.2,'mvoltage':1.92,'mpower':0.006})
avgdata.append({'mcurrent':12.3,'mvoltage':15.7,'mpower':0.19})
avgdata.append({'mcurrent':14.8,'mvoltage':26.7,'mpower':0.4})
avgdata.append({'mcurrent':16.3,'mvoltage':39.3,'mpower':0.64})
avgdata.append({'mcurrent':17.1,'mvoltage':48,'mpower':0.82})
avgdata.append({'mcurrent':17.7,'mvoltage':58.7,'mpower':0.84})
avgdata.append({'mcurrent':18,'mvoltage':70,'mpower':1.06})
avgdata.append({'mcurrent':19,'mvoltage':86,'mpower':1.33})
avgdata.append({'mcurrent':20,'mvoltage':120,'mpower':2.4})
avgdata.append({'mcurrent':20,'mvoltage':176,'mpower':3.52})
avgdata = pd.DataFrame(avgdata)
print(avgdata)

plt.close()

fig, (ax1, ax3) = plt.subplots(2,figsize=(4,2), sharex=True)

volt_color= 'tab:blue'
volt_style = 'solid'
amp_color = 'tab:red'
amp_style='dashed'
ax1.set_ylabel('Cell Voltage (mV)')
ax1.plot(avgdata.index, avgdata['mvoltage'], color=volt_color, ls=volt_style)
ax1.tick_params(axis='y', labelcolor=volt_color)
ax1.set_ylim(0, 200)

ax2 = ax1.twinx()
ax2.set_ylabel('Harvesting Current (μA)')
ax2.plot(avgdata.index, avgdata['mcurrent'], color=amp_color, ls=amp_style)
ax2.tick_params(axis='y', labelcolor=amp_color)
ax2.set_ylim(0,25)

ax1.tick_params(axis='x', which='both', length=0)
ax2.tick_params(axis='x', which='both', length=0)

ax1.grid(True)
ax1.legend(['voltage'], loc='lower right')
ax2.legend(['current'], loc='upper left')

ax3.set_ylabel("Power (uW)")
ax3.set_xlabel("Impedance ($\Omega$)")
ax3.grid(True)
ax3.set_ylim(0, 4)
ax3.plot(avgdata.index, avgdata['mpower'])
plt.xticks(np.arange(11), ['68', '100', '1k', '2k','3.3k','4.7k','6.8k','9.1k','15k','39k','82k'])

plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.5)
plt.subplots_adjust(hspace=0.15)
plt.savefig('c_impedance.pdf')
plt.close()

    
    
