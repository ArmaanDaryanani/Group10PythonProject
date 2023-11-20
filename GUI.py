"""
* Project 10, ENGR1110
* GUI File
* Last Updated 11/19/23
"""

# Add sidebar that ranks list of countries that will have the most deaths the next day
# Sidebar should be toggleable
# optimization


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import timedelta, datetime

from multiprocessing import Pool

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

#function to get latlong from full country name
def latlong(country_name):
    return country_data.get(country_name, (0, 0))  #default

def construct_data(deaths_filename):
    length_of_set = 0
    start_date_str = "2020-01-03"
    end_date_str = "2022-05-09"

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
        html.Button('Toggle Projection', id='toggle-projection-button'),
        dcc.Interval(
            id='interval-component',
            interval=3 * 1000,  # in milliseconds where 1*1000 means every second
            n_intervals=0,  # number of times the interval was activated
            max_intervals=-1,  # -1 means no limit
            disabled=True  # starts as disabled
        )
    ], style={'position': 'fixed', 'bottom': '2%', 'left': '2.5%', 'right': '2.5%'})
], style={'backgroundColor': 'white'})  # This line sets the background color of the entire webpage


country_names_list = []
country_by_lat = {}
#country is ISO3
with open("ISO3.txt", 'r') as file:
    for line in file:
        country = line.strip()
        country_names_list.append(country)
        full_name = ""
        with open("ISO3_Names.txt", 'r') as names:
            for names_line in names:
                list_of_names = names_line.split(":")
                if list_of_names[0].strip() == country:
                    full_name = list_of_names[1].strip()
        names.close()
        country_by_lat[latlong(full_name)[0]] = country

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def get_color(deaths, max_deaths):
    #>200,000
    if deaths > 200000:
        high_max_deaths = 1000000
        #interpolate between dark red and black
        light_red = (255, 0, 0)
        black = (0, 0, 0)
        normalized_high = clamp((deaths - 200000) / high_max_deaths, 0, 1)
        interpolated_rgb_high = tuple(
            int(light_red[i] + (black[i] - light_red[i]) * normalized_high) for i in range(3)
        )
        return f'rgb{interpolated_rgb_high}'
    #<100,000
    if deaths < 100000:
        dark_green = (35, 79, 30)
        light_green = (0, 255, 0)

        normalized_light = clamp(deaths / 100000, 0, 1)
        interpolated_rgb = tuple(
            int(dark_green[i] + (light_green[i] - dark_green[i]) * normalized_light) for i in range(3)
        )
        return f'rgb{interpolated_rgb}'

    else:
        #100,000-200,000
        light_green = (0, 255, 0)
        light_red = (255, 0, 0)
        normalized = clamp((deaths - 100000) / 100000, 0, 1)
        interpolated_rgb = tuple(
            int(light_green[i] + (light_red[i] - light_green[i]) * normalized) for i in range(3)
        )
        return f'rgb{interpolated_rgb}'

@app.callback(
    Output('world-map', 'figure'),
    [Input('date-slider', 'value'), Input('toggle-projection-button', 'n_clicks')],
    [State('world-map', 'figure')]
)
def update_map(date_index, toggle_clicks, current_fig):
    date = list(data.keys())[date_index]
    coords = data[date]
    new_coords_list = []
    traces = []
    deaths_by_country = {}

    if toggle_clicks is None:
        toggle_clicks = 0

    projection_type = "orthographic" if toggle_clicks % 2 != 0 else "mercator"

    #This loop will process the coordinates and separate the deaths
    for coord in coords:
        lat, long_deaths = coord
        len_deaths = int(str(long_deaths)[-1])
        deaths_str = str(long_deaths)[-(len_deaths + 1):-1]
        deaths = int(deaths_str)


        lat, long = coord
        length = len(str(long)) - (int(long[-1]) + 1)
        new_long = long[0:length]
        new_coord = (lat, new_long)
        new_coords_list.append(new_coord)
        print(long_deaths, deaths)

        for lat_country, country in country_by_lat.items():
            if lat_country == lat:
                deaths_by_country[country] = deaths

    "-----------------------------------"
    index = 0
    max_deaths = 200000
    for country in country_names_list:
        index += 1
        if index == 249:
            break
        else:
            print(country)
            mapped_value = 0.3
            rounded_mapped_val = round(mapped_value, 2)
            #print(deaths_by_country)
            deaths = deaths_by_country.get(country, 0)
            color = get_color(int(deaths), max_deaths)

            #create a copy for the specific country's geometry and simplify that
            country_geometry = gdf[gdf['ISO_A3'] == country].copy()
            country_geometry['geometry'] = country_geometry['geometry'].simplify(tolerance=rounded_mapped_val)
            simplified_geojson = json.loads(country_geometry.to_json())

            colored_country = go.Choropleth(
                geojson=simplified_geojson,
                locations=[country],
                z=[int(deaths)],
                colorscale=[[0, color], [1, color]],
                hoverinfo="location+z",
                showscale=False,
                featureidkey="properties.ISO_A3"
            )
            traces.append(colored_country)
    "-----------------------------------"

    center = {'lat': 0, 'lon': 0}


    # Layout of the map we are using
    layout = go.Layout(
        geo={
            'projection': {'type': projection_type},
            'center': center,
            'showland': True,
            'landcolor': '#234F1E',
            'showocean': True,
            'oceancolor': '#006994',
            'showcountries': False,
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