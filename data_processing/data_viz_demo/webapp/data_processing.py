import os
import ast
import numpy as np
import pandas as pd
from glob import glob
import formatting as fmt


# Fetches data in the form of split datasets
def fetch_data(working_dir, data_type):
    if data_type == 'teros':
        dataframes = split_data(load_and_process_TEROS_data(working_dir))

        sensor_data = dict()
        for k in dataframes.keys():
            sensor_data[k] = dataframe_to_xy_pairs(dataframes[k], 'timestamp', ['VWC', 'EC', 'temp']) # maybe smart way to not hardcode

        series = format_sensor_data_to_highcharts_compatible(sensor_data, data_type)
        return series
    else:
        dataframes = split_soil_dataframe(load_and_process_soil_data(working_dir))
        sensor_data = dict()
        for k in dataframes.keys():
            sensor_data[k] = dataframe_to_xy_pairs(dataframes[k], 'timestamp', ['voltage', 'current', 'power']) # maybe smart way to not hardcode

        series = format_sensor_data_to_highcharts_compatible(sensor_data, data_type)
        return series



####  From teros_plotter.py ####

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



# Loads our data, squishes it around a bit,  ---- and turns it into JSON for the webapp ----
def load_and_process_TEROS_data(working_dir, dset_name=''):
    # set up some paths
    pkl_dir = os.path.join(working_dir, "data", "pkls")					# directory to hold pickled data
    pkl_gen = os.path.join(pkl_dir, "*data*")
    pkl_file = os.path.join(pkl_dir, "teros_data.pkl")		# file name for pickled data
    pkl_meta = os.path.join(pkl_dir, "seen_datasets.txt")	# file name for list of pickled datasets

    data_gen = os.path.join(working_dir, "data", "TEROS*")

    print(pkl_file)


    # make our pickles directory if it doesn't already exist
    os.makedirs(pkl_dir, exist_ok=True)

    # # if we want to clear our original pickles, we delete the existing files
    # if args.c:
    #     old_pkls = glob(pkl_gen)
    #     for pkl_name in old_pkls:
    #         os.remove(pkl_name)


    # instantiate a dataframe for our teros data and a list of filenames for the datasets
    # in our data directory
    data_df = None
    new_datasets = set(glob(data_gen))
    # print(new_datasets)
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

        # Try to not convert the timestamp, see what happens
        #new_data['timestamp'] = new_data['timestamp'] * 1000 # need to convert to ms for javascript
        new_data['timestamp'] = pd.to_datetime(new_data['timestamp'], errors='coerce', unit='s')
        new_data['timestamp'] = new_data['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        new_data['timestamp'] = (new_data['timestamp'].astype(np.int64) / 1000000).astype(np.int64)
        #new_data['timestamp'] = new_data['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific').dt.strftime('%B %d, %Y, %r')
        #new_data.set_index('timestamp', inplace=True)

        # do some quick data cleaning to make sure we are getting numbers
        for column in new_data:
            if column != 'timestamp':
                new_data[column] = pd.to_numeric(new_data[column], errors='coerce')

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

        #data_df.to_pickle(pkl_file)
        #print("Saved new pickled data to '{}'".format(pkl_file))
       # _write_set(old_datasets.union(new_datasets), pkl_meta)
        #print("Saved new pickle metadata to '{}'".format(pkl_meta))

    # if we didn't load any data at all, print something saying so
    elif data_df is None:
        print("No TEROS data found. Returning None")

    # otherwise we just loaded up some data we already processed and saved, so we
    # don't need to save anything again
    else:
        print("Loaded previously processed data from '{}'".format(pkl_file))


    # return our dataframe for the next function to use
    return data_df


# takes a dataframe generated by load_and_process_data, takes out smaller dataframes based
# on sensorID
def split_data(data_df):
    # get a list of sensor IDs in our dataframe
    sensor_ids = data_df['sensorID'].unique()
    separate_sensor_data = dict()

    # for each sensor, subset out the relevant data and then plot and save said data
    for sensor_id in sensor_ids:
        separate_sensor_data[sensor_id] = data_df.loc[data_df['sensorID']==sensor_id]

    return separate_sensor_data



## From twobat_plot.py ##

def load_and_process_soil_data(working_dir):
    # set up some paths
    pkl_dir = os.path.join(working_dir, "data", "pkls")					# directory to hold pickled data
    pkl_gen = os.path.join(pkl_dir, "*data*")
    pkl_file = os.path.join(pkl_dir, "soil_data.pkl")		# file name for pickled data
    pkl_meta = os.path.join(pkl_dir, "seen_datasets.txt")	# file name for list of pickled datasets

    data_gen = os.path.join(working_dir, "data", "soil*")

    # print(pkl_file)

    if not os.path.exists(pkl_file):
        fnames = glob(os.path.join(working_dir, "data", "soil*.csv"))
        soil_data = None

        for fname in sorted(fnames, key=lambda x: int(x.split('.')[0].split('_')[-1])):
            # print(fname)
            data = np.genfromtxt(fname, dtype=float, delimiter=',',skip_header=11)
            data = pd.DataFrame({'timestamp':pd.to_datetime(data[:,0], unit='s'), 'current1':np.abs(data[:,4]*10E-12), 'voltage1':np.abs(data[:,5]*10E-9), 'current2':np.abs(data[:,8]*10E-12), 'voltage2':np.abs(data[:,6]*10E-9)})
            data['timestamp'] = data['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
            data['power1'] = np.abs(np.multiply(data['current1'], data['voltage1']))
            data['power2'] = np.abs(np.multiply(data['current2'], data['voltage2']))

            print(data['voltage1'][0:5])

            data.set_index('timestamp', inplace=True)

            # print(data)
            if soil_data is None:
                soil_data = data
            else:
                soil_data = pd.concat([soil_data, data])

        # print(soil_data)
        #soil_data.to_pickle("soil_data.pkl");
    else:
        soil_data = pd.read_pickle("soil_data.pkl")

    mv = soil_data.rolling(5*60).mean().dropna()

    return mv


def split_soil_dataframe(mv_dataframe):
    mv_dataframe['timestamp'] = (mv_dataframe.index.astype(np.int64) / 1000000).astype(np.int64)
    # Convert to two different sensors
    print(mv_dataframe['current1'][0])

    sensors = {1: pd.DataFrame({'timestamp':mv_dataframe['timestamp'], 'current':mv_dataframe['current1'], 'voltage':mv_dataframe['voltage1'], 'power':mv_dataframe['power1']}),
               2: pd.DataFrame({'timestamp':mv_dataframe['timestamp'], 'current':mv_dataframe['current2'], 'voltage':mv_dataframe['voltage2'], 'power':mv_dataframe['power2']})}

    #print(sensors[1].columns)

    return sensors


## Our utility methods

# Split the dataframe into pairs, so for each y_key, output an array of [[xval, yval], ...]
# Returns a dict where each key holds a 2d array formatted for highcharts
def dataframe_to_xy_pairs(data_df, x_key, y_keys):
    x_data = data_df[x_key].to_numpy()
    xy_data = dict()
    for k in y_keys:
        y_data = data_df[k].to_numpy()
        xy_data[k] = np.column_stack((x_data, y_data))
    return xy_data


# Takes a dict[sensorID->xy_pairs] and produces a properly formatted list
def format_sensor_data_to_highcharts_compatible(sensor_data, data_type):
    series = []
    for sensor_id in sensor_data.keys():
        for series_name in sensor_data[sensor_id].keys():
            series.append(fmt.data_array_to_highcharts_series_obj(sensor_data[sensor_id][series_name],
                                                              series_name,
                                                              sensor_id,
                                                              data_type))

    return series