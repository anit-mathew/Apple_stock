import pandas as pd
import json
import matplotlib.pyplot as plt

# JSON data (replacing the ellipsis with the actual data)
data = {
    'Meta Data': {
        '1. Information': 'Daily Prices (open, high, low, close) and Volumes',
        '2. Symbol': 'AAPL',
        '3. Last Refreshed': '2024-08-06',
        '4. Output Size': 'Compact',
        '5. Time Zone': 'US/Eastern'
    },
    'Time Series (Daily)': {
        '2024-08-06': {'1. open': '205.3000', '2. high': '209.9900', '3. low': '201.0700', '4. close': '207.2300', '5. volume': '66831777'},
        '2024-08-05': {'1. open': '199.0900', '2. high': '213.5000', '3. low': '196.0000', '4. close': '209.2700', '5. volume': '119548589'},
        '2024-08-02': {'1. open': '219.1500', '2. high': '225.6000', '3. low': '217.7100', '4. close': '219.8600', '5. volume': '105568560'},
        # more data here...
    }
}

# Convert the JSON data to a pandas DataFrame
time_series = data['Time Series (Daily)']
df = pd.DataFrame.from_dict(time_series, orient='index')
df.columns = ['open', 'high', 'low', 'close', 'volume']
df.index = pd.to_datetime(df.index)

# Convert string columns to float
df = df.astype(float)

# Plot the closing prices
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], marker='o')
plt.title('AAPL Closing Prices')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.grid(True)
plt.show()
