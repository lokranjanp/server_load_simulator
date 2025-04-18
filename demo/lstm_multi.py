import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load and preprocess
df = pd.read_csv('server_metrics.csv', parse_dates=['timestamp'])
df.set_index('timestamp', inplace=True)

# Keep relevant features
features = ['cpu_percent', 'memory_percent', 'load_avg', 'active_connections']
df = df[features].fillna(method='ffill')

# Normalize
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# Sequence creation
def create_sequences(data, target_index, window=30):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i - window:i])
        y.append(data[i, target_index])
    return np.array(X), np.array(y)

# Predicting cpu_percent (index 0)
target_index = 0
X, y = create_sequences(scaled_data, target_index)

# Train-test split
train_size = int(len(X) * 0.8)
X_train, y_train = X[:train_size], y[:train_size]
X_test, y_test = X[train_size:], y[train_size:]

# LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# Training
start_time = time.time()
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1, verbose=1)
training_time = time.time() - start_time

# Predict
predictions = model.predict(X_test)

# Metrics
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print(f"\nLSTM Results:")
print(f"Training Time: {training_time:.2f} seconds")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
