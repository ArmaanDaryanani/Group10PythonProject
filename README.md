# Neural Epidemiological Model and GUI

## **PLEASE REVIEW THE **IPYNB** FILE FOR MORE DETAILS!**

## Description
This project is a Python-based application that leverages neural networks, specifically through TensorFlow, to predict the global spread of viruses. It includes two main components: the frontend GUI and the backend neural processing.

## Team Members
- **Scrum Master:** Armaan Daryanani (AU 2026)
- **Product Owner:** Taylor Bagwell (AU 2027)
- **Developer 1:** Charlie Kemner (AU 2027)
- **Developer 2:** Ian Mcgrady (AU 2027)
- **Developer 3:** Raymond Dong (AU 2027)

## Project Overview
The **Neural Epidemiological Model** uses Long Short-Term Memory (LSTM) layers to predict viral spread based on three years of daily global data. The **GUI** is built using the Dash library, which allows for an interactive visualization of the model's predictions.

For full functionality, clone the repository from [GitHub](https://github.com/ArmaanDaryanani/Neural-Epidemiological-Modeling-and-GUI) and run it in a local environment.

## Dependencies
To install the required libraries for running the project:

```bash
pip install jupyter-dash plotly pycountry geopandas tensorflow
```

## GUI
The GUI component uses Dash for visualization. It displays an interactive world map that visualizes viral spread predictions. You can toggle between Mercator and Orthographic projections for different map views.

### Features:
- Date slider to visualize data over time
- Heatmaps to show viral spread intensity
- Toggle between different map projections

## Neural Processing
The neural network utilizes TensorFlow with multiple LSTM layers to forecast the next day's viral spread. The model processes daily data and predicts the number of deaths per country for the following day.

### Features:
- Three LSTM layers for time-series forecasting
- Dense output layer for final prediction
- Pretrained model for faster execution

## How to Run
1. Clone the repository from GitHub.
2. Install the required libraries.
3. Run the GUI application with:

```bash
python GUI.py
```

## Closing Notes
This project demonstrates the power of neural networks in modeling epidemiological data. While there is room for further improvements, the project serves as a stepping stone for future teams to expand on.


# PLEASE REVIEW THE **IPYNB** FILE FOR MORE DETAILS!
