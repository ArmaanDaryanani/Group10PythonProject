import tensorflow as tf
import numpy as np
from datetime import timedelta, datetime
from sklearn.preprocessing import MinMaxScaler
import joblib
from CaseProcessing import CaseProcessing

class NeuralProcessingTesting:
    def __init__(self):
        self.processor = CaseProcessing("total_deaths.txt")
        self.look_back = 1  # Consider making this a parameter
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def get_total_list(self, days_passed):
        startdate = "2020-01-03"
        start_date = datetime.strptime(startdate, '%Y-%m-%d')
        final_date = start_date + timedelta(days=days_passed)
        year, month, day = final_date.year, final_date.month, final_date.day
        death_list = self.processor.exclude_indexes(self.processor.get_country_deaths_dict(day, month, year), True)
        death_list.insert(0, days_passed)
        return death_list

    def prepare_dataset(self, dataset):
        # Add error handling or validations if necessary
        X, Y = [], []
        for i in range(len(dataset) - self.look_back):
            X.append(dataset[i:(i + self.look_back)])
            Y.append(dataset[i + self.look_back])
        return np.array(X), np.array(Y)

    def run_network(self):
        total_days = 1360
        dataset = [self.get_total_list(i) for i in range(total_days + 1)]
        dataset = self.scaler.fit_transform(dataset)

        X, Y = self.prepare_dataset(dataset)
        X = X.reshape(X.shape[0], self.look_back, -1)

        train_size = int(len(X) * 0.8)
        X_train, X_validate = X[:train_size], X[train_size:]
        Y_train, Y_validate = Y[:train_size], Y[train_size:]

        """MODEL"""
        my_model = tf.keras.models.Sequential()
        my_model.add(tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(self.look_back, len(self.get_total_list(1)))))
        my_model.add(tf.keras.layers.Dropout(0.2))
        my_model.add(tf.keras.layers.LSTM(64, return_sequences=True))
        my_model.add(tf.keras.layers.Dropout(0.2))
        my_model.add(tf.keras.layers.LSTM(32))
        my_model.add(tf.keras.layers.Dense(len(self.get_total_list(1))))
        my_model.compile(optimizer='adam', loss='mse')

        """TRAINING"""
        my_model.fit(X_train, Y_train, validation_data=(X_validate, Y_validate), epochs=30)

        joblib.dump(self.scaler, 'scaler.gz')
        self.predict_next(total_days, my_model)

    def predict_next(self, total_days, my_model):
        """PREDICTION"""
        last_day_data = np.array([self.get_total_list(total_days)])

        last_day_data = self.scaler.transform(last_day_data)
        last_day_data = last_day_data.reshape(1, self.look_back, -1)
        prediction_next_day = my_model.predict(last_day_data)
        prediction_next_day = self.scaler.inverse_transform(prediction_next_day)

        rounded_predictions = np.rint(prediction_next_day).astype(int)

        print("Prediction for the next day:", rounded_predictions)

        # what is should be:
        print(self.get_total_list(total_days + 1))

        if_save = input("Save Model? (y/n)")
        if if_save == "y":
            my_model.save("deaths_model")
        else:
            pass

neural_processor = NeuralProcessingTesting()
if_load = input("Load recent model? (y/n)")
if if_load == "y":
    my_model = tf.keras.models.load_model('deaths_model')
    neural_processor.scaler = joblib.load('scaler.gz')
    days_pass = input("What is your desired day?")
    neural_processor.predict_next(int(days_pass), my_model)
else:
    neural_processor.run_network()

