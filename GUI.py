"""
* Project 10, ENGR1110
* GUI File
* Last Updated 10/26/23
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import timedelta, datetime

import json
import geopandas as gpd



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
        file.close()
    return country_data



filename = "countries.txt"
country_data = read_data_from_file(filename)

with open('countries.geojson') as f:
    countries_geojson = json.load(f)

gdf = gpd.read_file('countries.geojson')

def initialize_color_country():
    country_dict = {}
    # lookup landmass and add to dictionary (country_ISO3 : country_position (on landmass)
    country_position = 0
    country_names = []
    country_ISO3_dict = {}
    with open("ISO3_Names.txt") as ISO3_file:
        for ISO3 in ISO3_file:
            names = ISO3.strip().split(":")
            country_ISO3_dict[names[1].strip()] = names[0].strip()
            country_names.append(names[1].strip())

    with open("countries_by_landmass.txt") as landmass_line:
        for landmass in landmass_line:
            landmass_list = landmass.strip().split("\t")
            for name in country_names:
                if name == landmass_list[1].strip():
                    country_dict[country_ISO3_dict[name]] = landmass_list[0]
    print(country_dict)
    return country_dict

country_dict = initialize_color_country()

def country_mapping(country_ISO3, country_dict):
    if country_dict.get(country_ISO3) is None:
        return 1
    else:
        country_position = int(country_dict[country_ISO3])
        print(f'{country_ISO3}:{country_position}')
        mapped_value = (1 - ((country_position - 1) / (199))) * (1.27) + 0.03
        if country_position >50:
            mapped_value = 0.2
        return mapped_value


#function to get latlong
def latlong(country_name):
    return country_data.get(country_name, (0, 0))  #default


def construct_data(deaths_filename):
    length_of_set = 0
    start_date_str = "2020-01-03"
    end_date_str = "2020-05-09"

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    processor = CaseProcessing(deaths_filename)  # Assuming CaseProcessing is defined elsewhere

    current_date = start_date
    data_dict = {}

    prev_latlong_values = set()  # We'll store the previous date's values here

    while current_date <= end_date:
        year, month, day = current_date.year, current_date.month, current_date.day
        country_deaths = processor.exclude_indexes(processor.get_country_deaths_dict(day, month, year))


        latlong_values = set()  # Initialize as an empty set for each day

        for country, deaths in country_deaths.items():
            if deaths > 0:
                # Get the lat-long pair for the country
                lat_long_pair = latlong(country)
                if lat_long_pair != (0, 0):
                    lat, long = lat_long_pair
                    latlong_values.add((lat, f'{long}{deaths}{len(str(deaths))}'))

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

all_countries = [country.name for country in pycountry.countries]

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='world-map',
        style={'height': '90vh', 'width': '95vw', 'margin': 'auto'}
    ),
    html.Div(id='globe-rotation', style={'display': 'none'}, children="{'lon': 0, 'lat': 0}"),

    html.Div([
        dcc.Slider(
            id='date-slider',
            min=0,
            max=len(data.keys()) - 1,
            value=0,
            step=None,
            marks=None  # Optional: marks for each step
        ),

        html.Button('Play', id='play-button'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds where 1*1000 means every second
            n_intervals=0,  # number of times the interval was activated
            max_intervals=-1,  # -1 means no limit
            disabled=True  # starts as disabled
        )
    ], style={'position': 'fixed', 'bottom': '2%', 'left': '2.5%', 'right': '2.5%'})
], style={'backgroundColor': 'white'})  # This line sets the background color of the entire webpage

country_names_list = []
with open("ISO3.txt", 'r') as file:
    for line in file:
        country = line.strip()
        country_names_list.append(country)




@app.callback(
    Output('world-map', 'figure'),
    [Input('date-slider', 'value')],
    [State('world-map', 'figure')]
)
def update_map(date_index, current_fig):
    date = list(data.keys())[date_index]
    coords = data[date]
    new_coords_list = []
    traces = []
    deaths_by_date = []

    # This loop will process the coordinates and separate the deaths
    for coord in coords:
        lat, long_deaths = coord
        len_deaths = "-" + str(long_deaths[-1])
        deaths = long_deaths[int(len_deaths)]
        deaths_by_date.append(deaths)  # Convert to int and store the deaths for the current date

        lat, long = coord
        length = len(str(long)) - (int(long[-1]) + 1)
        new_long = long[0:length]
        new_coord = (lat, new_long)
        new_coords_list.append(new_coord)

    new_coords_list = list(set(new_coords_list))

    center = {'lat': 0, 'lon': 0}
    projection = {'type': "orthographic"}

    if date_index > 0:  # Ensure there is a previous date to compare with

        prev_date = list(data.keys())[date_index - 1]
        prev_coords = data[prev_date]
        new_prev_coords = []
        for coord in prev_coords:
            lat, long = coord
            length = len(str(long)) - (int(long[-1]) + 1)
            new_long = long[0:length]
            new_coord = (lat, new_long)
            new_prev_coords.append(new_coord)

        new_prev_coords = list(set(new_prev_coords))

        # If the current date_index is beyond the first index, calculate the new points from two days ago.
        if date_index > 1:
            two_days_ago_date = list(data.keys())[date_index - 2]
            two_days_ago_coords = data[two_days_ago_date]
            new_two_days_ago_coords = []
            for coord in two_days_ago_coords:
                lat, long = coord
                length = len(str(long)) - (int(long[-1]) + 1)
                new_long = long[0:length]
                new_coord = (lat, new_long)
                new_two_days_ago_coords.append(new_coord)

            new_points_prev_day = set(new_prev_coords) - set(new_two_days_ago_coords)
            #print(new_points_prev_day)
        else:
            # If it's the first index, then all points from the previous day are considered new.
            new_points_prev_day = set(new_prev_coords)

        # Calculate new points for the current date
        new_points = set(new_coords_list) - set(new_prev_coords)

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
    for lon, lat in new_coords_list:
        traces.append(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            marker={'color': 'red', 'size': 10},
            mode='markers'
        ))

    # Layout of the map we are using
    layout = go.Layout(
        geo={
            'projection': projection,
            'center': center,
            'showland': True,
            'landcolor': '#234F1E',
            'showocean': True,
            'oceancolor': '#006994',
            'showcountries': True,
            'countrycolor': 'black',
            'countrywidth': 0.5,
            'showframe': False,
            'showcoastlines': True,
            'lataxis': {'range': [-60, 80]},
            'lonaxis': {'range': [-180, 180]}
        },
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        showlegend = False
    )

    "-----------------------------------"
    index = 0
    for country in country_names_list:
        index += 1
        if index == 50:  # Correctly use '==' for equality
            break
        else:
            print(country)
            mapped_value = country_mapping(country, country_dict)
            print(f"Mapped value for {country}: {mapped_value}")

            # Create a copy for the specific country's geometry and simplify that
            country_geometry = gdf[gdf['ISO_A3'] == country].copy()
            country_geometry['geometry'] = country_geometry['geometry'].simplify(tolerance=mapped_value)
            simplified_geojson = json.loads(country_geometry.to_json())

            colored_country = go.Choropleth(
                geojson=simplified_geojson,
                locations=[country],
                z=[0],  # Dummy data
                colorscale=[[0, '#1B7E10'], [1, '#1B7E10']],
                showscale=False,
                featureidkey="properties.ISO_A3"
            )
            traces.append(colored_country)

    "-----------------------------------"

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