
## HTML Generation ##
def generate_checkboxes_from_list(l):
    checkboxes = []
    for item in l:
        checkboxes.append(f'<div><input type="checkbox" id="{item}-cb" name="{item}" value="{item}"><label for="{item}-cb">{get_display_name(item)}</label></div>')
    return ''.join(checkboxes)

def generate_options_from_list(l):
    options = []
    for item in l:
        options.append(f'<option value="{item}">{get_display_name(item)}</option>')
    return ''.join(options)


def get_display_name(original_name):
    names_map = {"timestamp": "Time",
                 "VWC": "VWC",
                 "EC": "Conductivity",
                 "temp": "Temperature",
                 "voltage": "Voltage",
                 "current": "Current",
                 "power":   "Power",
                 }

    if original_name in names_map.keys():
        return names_map[original_name]
    return original_name


def y_axis_map(key, data_type):
    if data_type == 'teros':
        return y_axis_map_teros(key)
    else:
        return y_axis_map_soil(key)

def generate_y_axes_json(data_type):
    if data_type == 'teros':
        return generate_y_axes_teros_json()
    else:
        return generate_y_axes_soil_json()


def y_axis_map_teros(key):
    axis_map = {"VWC": 0,
                "EC": 1,
                "temp": 2
                }

    if key in axis_map.keys():
        return axis_map[key]
    return 0

def generate_y_axes_teros_json():
    y_axes = []
    y_axes.append(generate_y_axis('VWC', 0, False, ''))
    y_axes.append(generate_y_axis('EC', 1, True, 'mS/cm'))
    y_axes.append(generate_y_axis('temp', 2, True, '°C'))

    return y_axes



## Soil specific formatting

def y_axis_map_soil(key):
    axis_map = {"voltage": 0,
                "current": 1,
                "power": 2
                }

    if key in axis_map.keys():
        return axis_map[key]
    return 0

def generate_y_axes_soil_json():
    y_axes = []
    y_axes.append(generate_y_axis('voltage', 0, False, 'V'))
    y_axes.append(generate_y_axis('current', 1, True, 'μA'))
    y_axes.append(generate_y_axis('power', 2, True, 'μW'))

    return y_axes







def generate_y_axis(title, index, opposite, units, ax_min=0, ax_max=0):
    y_axis = {
        'labels': {
            'format': '{value}'+units,
            'style': {
                'color': 'Highcharts.getOptions().colors[2]'
            }
        },
        'title': {
            'text': title,
            'style': {
                'color': 'Highcharts.getOptions().colors[2]'
            }
        },
        'opposite': opposite#,
        #'min': min,
        #'max': max
    }
    return y_axis


def data_array_to_highcharts_series_obj(data, series_name, sensor_id, data_type):
    series = {
        'type': 'line',
        'name': f'{get_display_name(series_name)} (S{sensor_id})',
        'data': data.tolist(),
        'id': f'sensor{sensor_id}_{series_name}',
        'yAxis': y_axis_map_teros(series_name) if data_type == 'teros' else y_axis_map_soil(series_name)
    }
    return series


# Removes timestamp, raw_vwc, and sensor_id from a list
#   so that we don't display them for y axis selection in the visualizer
def remove_undesired_items(l):
    listset = set(l)
    undesired = {'timestamp', 'raw_VWC', 'sensorID' }
    return list(listset - undesired)