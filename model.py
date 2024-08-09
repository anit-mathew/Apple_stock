import os
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

import matplotlib.pyplot as plt

# Create directories if they don't exist
if not os.path.exists('static'):
    os.makedirs('static')
if not os.path.exists('templates'):
    os.makedirs('templates')

# Database connection parameters
db_config = {
    'user': 'admin',
    'password': '374EdtWCLdLrcvrdYTIi',
    'host': 'traffic-db.c7ee2qka2xm0.us-east-2.rds.amazonaws.com',
    'database': 'Apple_stock',
}

def fetch_data_from_db():
    connection = mysql.connector.connect(**db_config)
    query = "SELECT Date, Open, High, Low, Close, Volume FROM stock_data ORDER BY Date ASC"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def de_normalize_predictions(predictions, scaler, scaled_df):
    # Create a placeholder array with the same shape as the original scaled data
    placeholder = np.zeros((len(predictions), scaled_df.shape[1]))
    placeholder[:, 3] = predictions  # Only set the 'Close' column with the predictions
    inversed = scaler.inverse_transform(placeholder)
    return inversed[:, 3]  # Return only the 'Close' column

def predict_next_days(model, last_sequence, seq_length, days=10):
    predictions = []
    current_sequence = last_sequence.copy()
    for _ in range(days):
        next_day_prediction = model.predict(current_sequence.reshape(1, seq_length, -1))[0, 0]
        predictions.append(next_day_prediction)
        # Update sequence
        next_sequence = np.append(current_sequence[1:], [[next_day_prediction] * current_sequence.shape[1]], axis=0)
        current_sequence = next_sequence
    return predictions

def save_plot(dates, y_test, y_pred, future_dates, future_predictions_denormalized, last_date):
    plt.figure(figsize=(14, 7))
    plt.plot(dates, y_test, label='Actual Prices')
    plt.plot(dates, y_pred, label='Predicted Prices', linestyle='--')
    plt.title('Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.legend()
    plt.grid(True)
    plt.savefig('static/plot.png')  # Save the plot to a file

def main():
    df = fetch_data_from_db()
    print(df.head())

    # Convert Date to datetime and set it as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Feature engineering
    df['Previous_Close'] = df['Close'].shift(1)
    df.dropna(inplace=True)

    # Scale the data
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(df[['Open', 'High', 'Low', 'Close', 'Volume', 'Previous_Close']])
    scaled_df = pd.DataFrame(scaled_features, columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Previous_Close'], index=df.index)

    # Prepare sequences for LSTM
    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length, 3])  # Predicting 'Close' price
        return np.array(X), np.array(y)

    seq_length = 10
    X, y = create_sequences(scaled_df.values, seq_length)

    # Time Series Split
    tscv = TimeSeriesSplit(n_splits=5)

    mse_scores = []
    last_model = None

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        
        # Build and train the model
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')

        model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)

        # Evaluate the model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mse_scores.append(mse)
        last_model = model  # Save the last model for future use
        print(f'Mean Squared Error for Fold: {mse}')

    print(f'Average Mean Squared Error: {np.mean(mse_scores)}')

    # Final prediction for the next 10 days using the last fold's model
    last_sequence = scaled_df.values[-seq_length:]
    future_predictions = predict_next_days(last_model, last_sequence, seq_length)
    future_predictions_denormalized = de_normalize_predictions(future_predictions, scaler, scaled_df)

    # Generate future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date, periods=len(future_predictions) + 1, inclusive='right')


    # Plot results for the last fold
    dates = df.index[-len(y_test):]

    # Save the plot and predictions
    save_plot(dates, y_test, y_pred, future_dates, future_predictions_denormalized, last_date)

    # Save predictions to text file
    with open('static/predictions.txt', 'w') as f:
        f.write(f'Current Date: {last_date}\n')
        for date, prediction in zip(future_dates, future_predictions_denormalized):
            f.write(f'Date: {date}, Predicted Close Price: {prediction}\n')

    # Print the current date and future predictions with dates
    print(f'Current Date: {last_date}')
    for date, prediction in zip(future_dates, future_predictions_denormalized):
        print(f'Date: {date}, Predicted Close Price: {prediction}')

if __name__ == "__main__":
    main()
