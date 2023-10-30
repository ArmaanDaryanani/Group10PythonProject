"""
* Project 10, ENGR1110
* Neural Processing Testing File
* Last Updated 10/26/23
"""
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import timedelta, datetime

from CaseProcessing import CaseProcessing

processor = CaseProcessing("total_deaths.txt")
countries_by_deaths_list = processor.exclude_indexes(processor.get_country_deaths_dict("03","01","2020"))

def get_total_list(days_passed):
    startdate = "2020-01-03"
    start_date = datetime.strptime(startdate, '%Y-%m-%d')

    # Add days_passed to the start_date
    final_date = start_date + timedelta(days=days_passed)

    # Return the year, month, and day of the final date
    year = final_date.year
    month = final_date.month
    day = final_date.day

    return processor.exclude_indexes(processor.get_country_deaths_dict(day, month, year)).values()

def run_network():
    my_model = tf.keras.models.Sequential()

    my_model.add(tf.keras.layers.InputLayer(input_shape=(1+len(countries_by_deaths_list))))
    my_model.add(tf.keras.layers.Dense(128, return_sequences=True))
    my_model.add(tf.keras.layers.Dense(64, return_sequences=False))
    my_model.add(tf.keras.layers.Dense(32, activation='relu'))
    my_model.add(tf.keras.layers.Dense(1+len(countries_by_deaths_list)))

    my_model.compile(optimizer='adam', loss='mse')

    """training"""
    total_days = 100
    X = []
    Y = []

    for i in range(total_days):
        X.append([i] + get_total_list(i))
        Y.append(get_total_list(i+1))

    X = np.array(X)
    Y = np.array(Y)

    my_model.fit(X, Y, epochs=10)

    val_loss, val_acc = my_model.evaluate(X, Y)
    print('Test accuracy: ', val_acc)

run_network()





