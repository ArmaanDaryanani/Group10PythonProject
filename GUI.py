"""
* Project 10, ENGR1110
* GUI File
* Last Updated 10/19/23
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

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

filename = "countries.txt"
country_data = read_data_from_file(filename)

#function to get latlong
def latlong(country_name):
    return country_data.get(country_name, (0, 0))  #default

#data points dict example
data = {
    '2020-01-01': [latlong("China")],
    '2020-01-02': [latlong("China"), latlong("India")],
    '2020-01-03': [latlong("China"), latlong("India"), latlong("Thailand")],
    '2020-01-04': [latlong("China"), latlong("India"), latlong("Thailand"), latlong("Malaysia")],
    '2020-01-05': [latlong("China"), latlong("India"), latlong("Thailand"), latlong("Malaysia"), latlong("Vietnam"), latlong("Japan")],
    '2020-01-06': [latlong("China"), latlong("India"), latlong("Thailand"), latlong("Malaysia"), latlong("Vietnam"), latlong("Japan"), latlong("Australia"), latlong("South Korea")],
    '2020-01-07': [latlong("China"), latlong("India"), latlong("Thailand"), latlong("Malaysia"), latlong("Vietnam"), latlong("Japan"), latlong("Australia"), latlong("South Korea"), latlong("Russia"), latlong("Singapore"), latlong("Pakistan"), latlong("Turkey"), latlong("Mongolia"), latlong("Indonesia")]
}

all_countries = [country.name for country in pycountry.countries]

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='world-map',
        config={
            'staticPlot': True  #disables interactivity
        },
        style={'height': '90vh', 'width': '95vw', 'margin': 'auto'}
    ),
    html.Div([
        dcc.Slider(
            id='date-slider',
            min=0,
            max=len(data.keys()) - 1,
            value=0,
            marks={i: date for i, date in enumerate(data.keys())},
            step=None
        )
    ], style={'position': 'fixed', 'bottom': '2%', 'left': '2.5%', 'right': '2.5%'})
])

@app.callback(
    Output('world-map', 'figure'),
    [Input('date-slider', 'value')]
)
def update_map(date_index):
    date = list(data.keys())[date_index]
    coords = data[date]
    traces = []

    #connects the dots from the new points in the previous date to the new points in the current data
    for idx in range(1, date_index + 1):
        curr_date = list(data.keys())[idx]
        prev_date = list(data.keys())[idx - 1]

        curr_coords = data[curr_date]
        prev_coords = data[prev_date]

        #new points in the current date
        new_points_current_date = curr_coords[len(prev_coords):]

        #new points in the previous date
        if idx == 1:
            new_points_prev_date = [prev_coords[0]]  # only the first entry is new
        else:
            new_points_prev_date = prev_coords[len(data[list(data.keys())[idx - 2]]):]

        #connects every new point from the previous date to every new point in the current date
        for prev_lon, prev_lat in new_points_prev_date:
            for lon, lat in new_points_current_date:
                traces.append(go.Scattergeo(
                    lon=[prev_lon, lon],
                    lat=[prev_lat, lat],
                    mode='lines',
                    line={'color': 'blue', 'width': 1},
                ))

    #simple drawing of red dots for points
    for lon, lat in coords:
        traces.append(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            marker={'color': 'red', 'size': 10},
            mode='markers'
        ))

    #layout of the map we are using
    layout = go.Layout(
        geo={
            'projection': {'type': "mercator", 'scale': 1},
            'showland': True,
            'landcolor': 'green',
            'showcountries': True,
            'countrycolor': 'black',
            'countrywidth': 0.5,
            'center': {'lat': 30, 'lon': 0},
            'showframe': False,
            'showcoastlines': True,
            'lataxis': {'range': [-60, 80]},
            'lonaxis': {'range': [-180, 180]}
        },
        margin={"t": 0, "b": 0, "l": 0, "r": 0}
    )
    return {'data': traces, 'layout': layout}

#driver(can be moved to project driver)
if __name__ == '__main__':
    app.run_server(debug=False)
