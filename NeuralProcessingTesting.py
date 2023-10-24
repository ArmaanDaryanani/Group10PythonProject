"""
* Project 10, ENGR1110
* Neural Processing Testing File
* Last Updated 10/24/23
"""
import tensorflow as tf
import matplotlib.pyplot as plt
import os

day = 1
countries_by_deaths_list = [1,2,4,3,5,2,42,4,2,5,3,5,3,4,3,4,3,4,3,4,244,57,457,0,0,0,0,34,3242]

def run_network(self):
    my_model = tf.keras.models.Sequential([
        tf.keras.layers.Input(day, countries_by_deaths_list),
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense()
    ])
    my_model.compile(optimizer='adam', loss='mse')

    """training"""
    my_model.fit()

def get_list(filename, day):
    with open(filename, 'r') as file:
        num_lines = 0
        num_days = 0

        for line in file:
            if num_lines == 0:
                num_lines += 1
                countries_list = []
                num_countries = 0
                line_list = line.split(",")
                for val in line_list:
                    match val:
                        case "date":
                            continue
                        case "World":
                            continue
                        case _:
                            num_countries+=1
                            countries_list.append(val)

                print(countries_list)
                print(num_countries)
                continue
            else:
                num_days += 1
                num_lines += 1
                year = line[0:4]
                month = line[5:7]
                day = line[8:10]

                death_list = []
                for val in line.split(","):
                    if val == "":
                        death_list.append("0")
                    else:
                        death_list.append(val)
                print(death_list)


        print(num_days)


def get_list_size(self):
    return len(self.get_list)


get_list("total_deaths.txt", 1)
