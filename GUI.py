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

filename = "countries.txt"
country_data = read_data_from_file(filename)

#function to get latlong
def latlong(country_name):
    return country_data.get(country_name, (0, 0))  #default

def construct_data(deaths_filename):
    start_date_str = "2020-01-03"
    end_date_str = "2020-05-09"

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    processor = CaseProcessing(deaths_filename)

    current_date = start_date
    data_dict = {}

    prev_latlong_values = set()  # We'll store the previous date's values here

    while current_date <= end_date:
        year, month, day = current_date.year, current_date.month, current_date.day
        country_deaths = processor.exclude_indexes(processor.get_country_deaths_dict(day, month, year))

        # Get country names with deaths > 0
        countries_with_deaths = [country for country, deaths in country_deaths.items() if deaths > 0]

        # Get the latlong values for these countries
        latlong_values = set([latlong(country) for country in countries_with_deaths])

        # Remove (0, 0) from the list if it's present
        latlong_values.discard((0, 0))

        date_str = current_date.strftime('%Y-%m-%d')

        # Find new points that weren't in the previous day's data
        new_points = latlong_values - prev_latlong_values

        # If there are new points, update the data dictionary for the day
        if new_points:
            # Combine new points with previous points, placing new points at the top
            combined_points = list(prev_latlong_values) + list(new_points)
            data_dict[date_str] = combined_points

        prev_latlong_values = latlong_values

        # Move to the next date
        current_date += timedelta(days=1)
    print(data_dict)
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
            step=1  # Changed from None to 1
        ),
        html.Button('Play', id='play-button'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds; 1*1000 means every second
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
    coords = data[date]
    traces = []

    if date_index > 0:  # Ensure there is a previous date to compare with
        prev_date = list(data.keys())[date_index - 1]
        prev_coords = data[prev_date]

        # If the current date_index is beyond the first index, calculate the new points from two days ago.
        if date_index > 1:
            two_days_ago_date = list(data.keys())[date_index - 2]
            two_days_ago_coords = data[two_days_ago_date]
            new_points_prev_day = set(prev_coords) - set(two_days_ago_coords)
        else:
            # If it's the first index, then all points from the previous day are considered new.
            new_points_prev_day = set(prev_coords)

        # Calculate new points for the current date
        new_points = set(coords) - set(prev_coords)

        # Draw lines between the new points of the current date and the new points from the previous day
        for lon, lat in new_points:
            for prev_lon, prev_lat in new_points_prev_day:
                traces.append(go.Scattergeo(
                    lon=[prev_lon, lon],
                    lat=[prev_lat, lat],
                    mode='lines',
                    line={'color': 'blue', 'width': 1},
                ))

    # Draw the current points
    for lon, lat in coords:
        traces.append(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            marker={'color': 'red', 'size': 10},
            mode='markers'
        ))

    # Layout of the map we are using
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
            'lonaxis': {'range': [-180, 180]},
            'bgcolor': 'lightblue'
        },
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        showlegend = False
    )
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
