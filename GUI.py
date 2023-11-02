"""
* Project 10, ENGR1110
* GUI File
* Last Updated 10/31/23
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import timedelta, datetime

import json

with open('countries.geojson') as f:
    countries_geojson = json.load(f)


import pandas as pd
import plotly.express as px

from CaseProcessing import CaseProcessing

import pycountry

#reads filename data and stores as dict
def read_data_from_file(filename):
    country_data = {}
    with open(filename, 'r') as file:
        for line in file:
            split_line = line.strip().split("\t")
            country_code, lon, lat, country_name = split_line
            country_data[country_name] = (lat, lon)
    return country_data

"""---------------------"""
filename = "countries.txt"
country_data = read_data_from_file(filename)
start_date_str = "2020-01-03"
end_date_str = "2020-05-09"

processor = CaseProcessing("total_deaths.txt")

lon_data = {}
with open(filename, 'r') as file:
    for line in file:
        split_line = line.strip().split("\t")
        country_code, lon, lat, country_name = split_line
        lon_data[lat] = country_name
"""---------------------"""

#function to get latlong
def latlong(country_name):
    return country_data.get(country_name, (0, 0))  #default

def scale_deaths(deaths, min_size=2, max_size=15):
    #scale deaths to a range of 1-20 for marker size
    max_possible_deaths = 100000
    if deaths > max_possible_deaths:
        scaled_deaths = max_size
    elif deaths <= 0:
        scaled_deaths = min_size
    else:
        scaled_deaths = min_size + (max_size - min_size) * (deaths / max_possible_deaths)

    return scaled_deaths


def construct_data(deaths_filename="total_deaths.txt"):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    current_date = start_date
    data_dict = {}

    prev_latlong_values = set()

    while current_date <= end_date:
        year, month, day = current_date.year, current_date.month, current_date.day
        country_deaths = processor.exclude_indexes(processor.get_country_deaths_dict(day, month, year))

        # get country names with deaths > 0 and the corresponding death counts
        countries_with_deaths = [(country, deaths) for country, deaths in country_deaths.items() if deaths > 0]

        # get the latlong values and death counts for these countries
        latlong_values = set([(latlong(country), deaths) for country, deaths in countries_with_deaths])

        # remove (0, 0) from the list if it's present
        latlong_values.discard(((0, 0), 0))

        date_str = current_date.strftime('%Y-%m-%d')

        # find new points that weren't in the previous day's data
        new_points = latlong_values - prev_latlong_values

        # if there are new points, update the data dictionary for the day
        if new_points:
            # combine new points with previous points, placing new points at the top
            combined_points = list(prev_latlong_values) + list(new_points)
            data_dict[date_str] = combined_points

        prev_latlong_values = latlong_values

        # move to the next date
        current_date += timedelta(days=1)

    return data_dict

#data points dict
data = construct_data("total_deaths.txt")

print(construct_data("total_deaths.txt"))

all_countries = [country.name for country in pycountry.countries]

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='world-map',
        config={
            'staticPlot': False  #disables interactivity
        },
        style={'height': '90vh', 'width': '95vw', 'margin': 'auto'}
    ),
    html.Div([
        dcc.Slider(
            id='date-slider',
            min=0,
            max=len(data.keys()) - 1,
            value=0,
            step=1  # Changed from None to 1
        ),
        html.Button('Play', id='play-button'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 200,  # in milliseconds; 1*1000 means every second
            n_intervals=0,  # number of times the interval was activated
            max_intervals=-1,  # -1 means no limit
            disabled=True  # starts as disabled
        )
    ], style={'position': 'fixed', 'bottom': '2%', 'left': '2.5%', 'right': '2.5%'})
], style={'backgroundColor': 'white'})  # This line sets the background color of the entire webpage


@app.callback(
    Output('world-map', 'figure'),
    [Input('date-slider', 'value')]
)
def update_map(date_index):
    date = list(data.keys())[date_index]
    coords_with_deaths = data[date]
    traces = []

    for (lon, lat), deaths in coords_with_deaths:  # Unpack each item
        if date_index > 0:  # Ensure there is a previous date to compare with
            prev_date = list(data.keys())[date_index - 1]
            prev_coords_with_deaths = data[prev_date]

            prev_coords = [(prev_lon, prev_lat) for (prev_lon, prev_lat), _ in prev_coords_with_deaths]

            # If the current date_index is beyond the first index, calculate the new points from two days ago.
            if date_index > 1:
                two_days_ago_date = list(data.keys())[date_index - 2]
                two_days_ago_coords_with_deaths = data[two_days_ago_date]
                two_days_ago_coords = [(two_days_ago_lon, two_days_ago_lat) for (two_days_ago_lon, two_days_ago_lat), _ in two_days_ago_coords_with_deaths]
                new_points_prev_day = set(prev_coords) - set(two_days_ago_coords)
            else:
                # If it's the first index, then all points from the previous day are considered new.
                new_points_prev_day = set(prev_coords)

            # Calculate new points for the current date
            new_points = set([(lon, lat)]) - set(prev_coords)

            # Draw lines between the new points of the current date and the new points from the previous day
            for new_lon, new_lat in new_points:
                for prev_lon, prev_lat in new_points_prev_day:
                    traces.append(go.Scattergeo(
                        lon=[prev_lon, new_lon],
                        lat=[prev_lat, new_lat],
                        mode='lines',
                        line={'color': 'blue', 'width': 1},
                    ))

        # Draw the current points
        traces.append(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            marker={'color': 'red', 'size': scale_deaths(deaths)},
            mode='markers'
        ))
    # Layout of the map we are using
    layout = go.Layout(
        geo={
            'projection': {'type': "orthographic"},
            'showland': True,
            'landcolor': 'gray',
            'showcountries': True,
            'countrycolor': 'black',
            'countrywidth': 0.5,
            'center': {'lat': 30, 'lon': 0},
            'showframe': False,
            'showcoastlines': True,
            'lataxis': {'range': [-60, 80]},
            'lonaxis': {'range': [-180, 180]},
            'bgcolor': 'white',
            'showsubunits': True
        },
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        showlegend = False
    )

    usa_trace = go.Choropleth(
        geojson=countries_geojson,
        locations=['USA'],
        z=[0],  # Dummy data
        colorscale=[[0, 'green'], [1, 'green']],
        showscale=False,
        featureidkey="properties.ISO_A3"  # Adjust according to your GeoJSON structure
    )
    traces.append(usa_trace)

    return {'data': traces, 'layout': layout}
@app.callback(
    Output('date-slider', 'value'),
    [Input('interval-component', 'n_intervals')],
    [State('date-slider', 'value')]
)
def update_slider(n, current_value):
    if current_value < len(data.keys()) - 1:
        return current_value + 1
    else:
        return current_value

@app.callback(
    [Output('interval-component', 'disabled'),
     Output('play-button', 'children')],
    [Input('play-button', 'n_clicks')],
    [State('interval-component', 'disabled')]
)
def toggle_play(n_clicks, currently_disabled):
    if n_clicks is None:  # the button was never clicked
        return True, "Play"

    if currently_disabled:
        return False, "Pause"
    else:
        return True, "Play"
#driver(can be moved to project driver)
if __name__ == '__main__':
    app.run_server(debug=False)
