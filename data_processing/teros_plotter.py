#!/usr/bin/env python3

# Written for the WaterSystems collaboration (UC Berkeley, Stanford, and Northwestern)
# by Alvin Tan on 11/16/2020

# Plots temperature, electric conductivity, and volumetric moisture values
# collected by a TEROS device
# Converts raw TEROS moisture data into volumetric moisture measurements
# (see TEROS 11/12 manual section 4 for more details on calibration:
#  http://publications.metergroup.com/Manuals/20587_TEROS11-12_Manual_Web.pdf)

import os
import ast
import argparse
import numpy as np
import pandas as pd
from glob import glob
from matplotlib import pyplot as plt


# This is our soil-specific calibration to convert from raw moisture measurements to 
# volumetric moisture values
def _raw_to_vm(rawBoi):
	return (9.079e-10)*rawBoi**3 - (6.626e-6)*rawBoi**2 + (1.643e-2)*rawBoi - 1.354e1

# A couple helper functions used to write metadata to save some time
def _write_set(set_boi, file_name):
	with open(file_name, "w") as f:
		f.write(str(set_boi))
	return	# an empty return here just to make me feel better about the 'with' statement

def _load_set(file_name):
	with open(file_name, 'r') as f:
		meta_set = ast.literal_eval(f.read())
	return meta_set

# Loads our data, squishes it around a bit, and saves it as a pickle 
def load_and_process_data(args):
	# set up some paths
	pkl_dir = os.path.join(args.dd, "pkls")					# directory to hold pickled data
	pkl_gen = os.path.join(pkl_dir, "*data*")
	pkl_file = os.path.join(pkl_dir, "teros_data.pkl")		# file name for pickled data
	pkl_meta = os.path.join(pkl_dir, "seen_datasets.txt")	# file name for list of pickled datasets
	
	data_gen = os.path.join(args.dd, args.dn)
	
	
	# make our pickles directory if it doesn't already exist
	os.makedirs(pkl_dir, exist_ok=True)
	
	# if we want to clear our original pickles, we delete the existing files
	if args.c:
		old_pkls = glob(pkl_gen)
		for pkl_name in old_pkls:
			os.remove(pkl_name)
	
	
	# instantiate a dataframe for our teros data and a list of filenames for the datasets 
	# in our data directory
	data_df = None
	new_datasets = set(glob(data_gen))
	old_datasets = set()
	
	# if we've already done data processing before, we can load in the previously processed
	# data and ignore any dataset files that we have already processed
	if os.path.exists(pkl_meta) and os.path.exists(pkl_file):
		data_df = pd.read_pickle(pkl_file)
		old_datasets = _load_set(pkl_meta)
		new_datasets -= old_datasets
	
	#dtypes = {'timestamp':np.int64, 'sensorID':np.int64, 'raw_VWC':np.float64, 'temp':np.float64, 'EC':np.int64}
	# now load in new datasets, squish them around a bit, and add them to our dataframe
	for data_name in sorted(new_datasets, key=lambda x: int(x.split('-')[-2])):
		print("Loading and processing data from '{}'".format(data_name))	# print the dataset we are loading in for debugging purposes
		new_data = pd.read_csv(data_name)#, dtype=dtypes)
		
		new_data['timestamp'] = pd.to_datetime(new_data['timestamp'], errors='coerce', unit='s')
		new_data['timestamp'] = new_data['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
		new_data.set_index('timestamp', inplace=True)
		
		# do some quick data cleaning to make sure we are getting numbers
		for column in new_data:
			new_data[column] = pd.to_numeric(new_data[column], errors='coerce')

		breakpoint()
		
		# drop any NaN values from junky data 
		new_data.dropna()
		
		# calculate our volumetric moisture values from raw moisture measurements
		new_data['VWC'] = _raw_to_vm(new_data['raw_VWC'])
		# would it be faster to concatenate all the new datasets together before doing
		# this operation?
		
		# add our new data to the full dataframe
		data_df = pd.concat([data_df, new_data])
	
	
	# if we added new datasets, then we should sort, pickle, and save our dataframe
	if new_datasets:
		# Note: we loaded data in the order of dataset file creation time (done with the
		# 'sorted' function in the 'for' statement above), so we might not have to sort
		# the dataframe here (i.e. the dataframe may already be sorted by construction)
		data_df.sort_index(inplace=True, kind='heapsort')
		
		data_df.to_pickle(pkl_file)
		print("Saved new pickled data to '{}'".format(pkl_file))
		_write_set(old_datasets.union(new_datasets), pkl_meta)
		print("Saved new pickle metadata to '{}'".format(pkl_meta))
	
	# if we didn't load any data at all, print something saying so
	elif data_df is None:
		print("No TEROS data found. Returning None")
	
	# otherwise we just loaded up some data we already processed and saved, so we
	# don't need to save anything again
	else:
		print("Loaded previously processed data from '{}'".format(pkl_file))
	
	
	# return our dataframe for the next function to use
	return data_df
	


# takes a dataframe containing data from only one sensor
# plots temperature, electrical current, and volumetric moisture values over time
# saves figures as png files in the designated directory
def _plot_and_save_data(args, data_df):

	breakpoint()
	
	# grab some descriptive information
	sensor_id = data_df['sensorID'].iat[0]
	start_time = data_df.index[0]
	end_time = data_df.index[-1]
	
	
	# setup some paths
	fig_dir = os.path.join(args.dd, "figs")
	fig_file = os.path.join(fig_dir, "sensor-{}_from-{}_to-{}.{}".format(sensor_id, start_time, end_time, args.ft))
	# make the figures directory if it doesn't already exist
	os.makedirs(fig_dir, exist_ok=True)
	
	
	# make our plot
	plt.figure()
	plt.suptitle("Sensor {} data from {} to {}".format(sensor_id, start_time, end_time))

	plt.subplot(311)
	#plt.xlabel("Time")
	plt.ylabel("Temperature (C)")
	plt.plot(data_df.index, data_df['temp'])
	
	plt.subplot(312)
	#plt.xlabel("Time")
	plt.ylabel("Electrical Conductivity")
	plt.plot(data_df.index, data_df['EC'])
	
	plt.subplot(313)
	plt.xlabel("Time")
	plt.ylabel("Volumetric Moisture Content")
	plt.plot(data_df.index, data_df['VWC'])
	
	
	# display and save our plot
	plt.show()
	plt.savefig(fig_file)
	print("Figure saved to '{}'".format(fig_file))

# takes a dataframe generated by load_and_process_data, takes out smaller dataframes based
# on sensorID, and feeds said smaller dataframe to _plot_and_save_data to be visualized
def split_and_plot_data(args, data_df):
	# get a list of sensor IDs in our dataframe
	sensor_ids = data_df['sensorID'].unique()
	
	# for each sensor, subset out the relevant data and then plot and save said data 
	for sensor_id in sensor_ids:
		sensor_data = data_df.loc[data_df['sensorID']==sensor_id]
		_plot_and_save_data(args, sensor_data)
	
	print("Done plotting all the data in our dataframe")



# main function that parses out command line inputs and feeds it into the
# corresponding functions
if __name__ == "__main__":
	# describe the optional command line inputs we are looking for
	parser = argparse.ArgumentParser(description='Plot TEROS data')
	
	parser.add_argument('-dd', type=str, default="data/teros",
						help="data directory (default is 'data/teros')")
	
	parser.add_argument('-dn', type=str, default="TEROSoutput*.csv",
						help="datafile name (default is 'TEROSoutput*.csv')")
	
	parser.add_argument('-c', action='count', default=0,
						help="delete all existing pickles before processing data")
	
	parser.add_argument('-ft', type=str, default="png",
						help="figure type (default is 'png')")


	# parse out command line inputs
	args = parser.parse_args()

	# load in our data and put it in a dataframe
	data_df = load_and_process_data(args)

	# plot our data and save the plots 
	split_and_plot_data(args, data_df)



















