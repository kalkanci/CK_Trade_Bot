# models.py

import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from config import SEQUENCE_LENGTH, EPOCHS, BATCH_SIZE

class PricePredictionModel:
    def __init__(self):
        self.model = self._create_model()
        self.scaler = MinMaxScaler()

    def _create_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(SEQUENCE_LENGTH, 5)),
            tf.keras.layers.LSTM(50, return_sequences=False),
            tf.keras.layers.Dense(25),
            tf.keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def prepare_data(self, df):
        # Özellik seçimi
        features = ['close', 'volume', 'RSI', 'MACD', 'Signal']
        dataset = df[features].values
        
        # Veriyi normalize et
        scaled_data = self.scaler.fit_transform(dataset)
        
        # Eğitim verisi oluştur
        X = []
        y = []
        for i in range(SEQUENCE_LENGTH, len(scaled_data)):
            X.append(scaled_data[i-SEQUENCE_LENGTH:i])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)

    def train(self, df):
        X, y = self.prepare_data(df)
        self.model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=0)

    def predict(self, df):
        # Son SEQUENCE_LENGTH kadar veriyi al
        last_sequence = df.tail(SEQUENCE_LENGTH)
        features = ['close', 'volume', 'RSI', 'MACD', 'Signal']
        sequence = last_sequence[features].values
        
        # Veriyi normalize et
        scaled_sequence = self.scaler.transform(sequence)
        
        # Tahmin için yeniden şekillendir
        X = scaled_sequence.reshape((1, SEQUENCE_LENGTH, 5))
        
        # Tahmin yap
        prediction = self.model.predict(X)
        
        # Tahmini gerçek değere dönüştür
        prediction_transformed = self.scaler.inverse_transform(
            np.array([[prediction[0, 0], 0, 0, 0, 0]])
        )[0, 0]
        
        return prediction_transformed