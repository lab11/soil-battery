#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from pytz import timezone
import pandas as pd
from glob import glob
import arrow

fnames = glob("data/soil*.csv")
soil_data = None

for fname in sorted(fnames, key=lambda x: int(x.split('.')[0].split('_')[-1])):
    print(fname)
    data = np.genfromtxt(fname, dtype=float, delimiter=',',skip_header=11)
    data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current':data[:,2]*1E-9, 'voltage':data[:,4]*10E-9})
    data.timestamp = data.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    data['power'] = np.abs(np.multiply(data['current'], data['voltage']))
    data.set_index('timestamp', inplace=True)
    print(data)
    if soil_data is None:
        soil_data = data
    else:
        soil_data = pd.concat([soil_data, data])

print(soil_data)

mv = soil_data.rolling(5*60).mean()
fig, ax = plt.subplots(figsize=(12,6))
fig.autofmt_xdate()
ax.fmt_xdata = md.DateFormatter('%d %h:%m')
plt.grid(True)
plt.title("Soil Energy Harvesting")
plt.xlabel("Time")
plt.ylabel("Power (uW)")
plt.plot(mv.index, 1E6*mv['power'])
plt.tight_layout()
plt.savefig('soil.pdf')
#plt.savefig('soil.png', dpi=180)
tot_energy = np.trapz(soil_data['power'])
print(tot_energy)
print((soil_data.tail(1).index - soil_data.head(1).index).total_seconds())
