"""
* Project 10, ENGR1110
* Neural Processing Testing File
* Last Updated 10/26/23
"""
import tensorflow as tf
import matplotlib.pyplot as plt
import os
from datetime import timedelta, datetime

from CaseProcessing import CaseProcessing

processor = CaseProcessing("total_deaths.txt")
countries_by_deaths_list = processor.exclude_indexes(processor.get_country_deaths_list_per_date("03","01","2020"))

def get_total_list(days_passed):
    startdate = "2020-01-03"
    start_date = datetime.strptime(startdate, '%Y-%m-%d')

    # Add days_passed to the start_date
    final_date = start_date + timedelta(days=days_passed)

    # Return the year, month, and day of the final date
    year = final_date.year
    month = final_date.month
    day = final_date.day



def run_network(self):
    my_model = tf.keras.models.Sequential([

        tf.keras.layers.Input(day, len(countries_by_deaths_list)),
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense()
    ])
    my_model.compile(optimizer='adam', loss='mse')

    """training"""
    my_model.fit()





