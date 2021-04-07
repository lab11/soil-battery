TEROSoutput-\*.csv files have soil moisture, electrical conductivity and temperature measurements from the buried Teros12 sensors. 
Each file has measurements from two sensors. The data format is timestamp,sensorID,raw_VWC,temp,EC. Sensor ID corresponds to the 
SDI serial address of the sensor, so for our setup it will be 0 or 1. The raw_VWC needs to be converted to a percent...
(typical values are between 0 and 50-60%), the conversion process is soil-specific, so there should be two different equations, 
one for Stanford, one for NW. More info on sensor values is in the Teros manual: http://www.misure.net/sites/default/files/pdf/20587_TEROS%2012_Manual_Web.pdf
For an example of how to plot these values, see soil-battery/data_processing/teros_plotter.py.

soil_\*\_N.csv files are current and voltage measurements from the rocketloggers. Each file has data from two batteries. The data format is
timestamp [epoch],I1L_valid,I2L_valid,I1H [nA],I1L [10pA],V1 [10nV],V2 [10nV],I2H [nA],I2L [10pA]. The best resource for learning how to work with this data is
by looking at the existing python plotting scripts in soil-battery/data_processing. In particular, we mainly use twobat_plot.py.


