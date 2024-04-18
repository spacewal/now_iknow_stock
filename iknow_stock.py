# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Z5A5CcxvnZwFJJDg2q1Ul8MFGq0OvxjM
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt
from tensorflow.keras.models import load_model
import numpy as np
import pickle

# Load scaler and model
# Load scaler and model
@st.cache(allow_output_mutation=True)
def load_assets():
    scaler_path = 'scaler.pkl'
    model_path = 'best_model.keras'

    # Load scaler
    with open(scaler_path, 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)

    # Load model
    model = load_model(model_path)

    return scaler, model

# Preprocess data
def preprocess_data(stock_data, scaler):
    stock_data.fillna(method='ffill', inplace=True)  # Forward-fill to handle missing values
    closing_prices = stock_data['Close'].values.reshape(-1, 1)
    scaled_data = scaler.transform(closing_prices)
    X = []
    for i in range(60, len(scaled_data)):
        X.append(scaled_data[i-60:i, 0])
    X = np.array(X)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X

# Main page setup
st.title('S&P 500 Stock Price Prediction')

# Fetch S&P 500 tickers
sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
sp500['Symbol'] = sp500['Symbol'].str.replace('.', '-')
symbols_list = sp500['Symbol'].unique().tolist()

# Selectbox for the user to choose the stock symbol
selected_symbol = st.selectbox('Select a stock symbol:', symbols_list)

# Load model and scaler
scaler, model = load_assets()

# Get the date range for downloading historical data
end_date = dt.datetime.now()
start_date = end_date - pd.DateOffset(days=365*8)

# Download data and make prediction
if st.button('Predict'):
    with st.spinner('Fetching historical data...'):
        df = yf.download(selected_symbol, start=start_date, end=end_date)
        st.success('Historical data fetched!')

        with st.spinner('Preprocessing data...'):
            X = preprocess_data(df, scaler)
            st.success('Data preprocessed!')

            with st.spinner('Predicting future prices...'):
                predicted_price = model.predict(X[-1:])  # Predict using the last sequence
                predicted_price = scaler.inverse_transform(predicted_price)  # Inverse scaling to get actual price
                st.success('Prediction complete!')

                # Display the prediction
                st.write(f"The predicted closing price for {selected_symbol} is ${predicted_price[0][0]:.2f}")

# Run the main function
if __name__ == '__main__':
    main()