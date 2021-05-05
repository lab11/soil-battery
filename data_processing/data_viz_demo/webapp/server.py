# Main server file for data visualization webapp

from flask import Flask, render_template, request, jsonify
import os
import ast
import argparse
import numpy as np
import pandas as pd
from glob import glob
import formatting as fmt
import data_processing as dp\

working_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

# set the project root directory as the static folder, you can set others.
app = Flask (__name__,
             static_url_path='',
             static_folder='web/static')

@app.route('/')
def serve_static():
    names, sensor_ids, fields = setup()
    return render_template("templates/index.html", dataset_dropdown=names, sensor_id_checkboxes=sensor_ids, series_name_checkboxes=fields)


@app.route('/api/get_chart_data')
def get_chart_data():
    data_type = get_data_config_from_request(request.args)
    series = dp.fetch_data(working_dir, data_type)
    y_axes = fmt.generate_y_axes_json(data_type)

    highcharts_json_obj = create_get_chart_data_response_obj(series, y_axes)

    return highcharts_json_obj


# Create get_chart_data response object
def create_get_chart_data_response_obj(series, y_axes):
    json_response = dict()
    json_response['series'] = series
    json_response['yaxes'] = y_axes
    return jsonify(json_response)



### SETUP and INIT VALS ###

# Returns variably generated html to populate the index webpage with to display data
def setup():
    setup_data = get_setup_data()
    names, sensor_ids, fields = generate_setup_html(setup_data)
    return names, sensor_ids, fields

# Loads in existing datasets and prepares the lists of what data to display to the user
def get_setup_data():
    dataframes = dp.split_data(dp.load_and_process_TEROS_data(working_dir))
    sensor_fields = fmt.remove_undesired_items(list(dataframes[0].columns))
    sensor_names = ["teros", "soil"]
    sensor_ids = dataframes.keys()
    setup_data = {"names": sensor_names,
                  "sensor_ids": sensor_ids,
                  "fields": sensor_fields}
    return setup_data

def generate_setup_html(setup_data):
    names = fmt.generate_options_from_list(setup_data["names"])
    sensor_ids = fmt.generate_checkboxes_from_list(setup_data["sensor_ids"])
    fields = fmt.generate_checkboxes_from_list(setup_data["fields"])

    return names, sensor_ids, fields


# Parse the expected request object in the path /get_chart_data
def get_data_config_from_request(args):
    data_type = None
    if 'data_type' in args:
        data_type = args["data_type"]
    return data_type


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

if __name__ == "__main__":
    app.run()


