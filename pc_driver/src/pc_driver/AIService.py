from typing import List
import json
import glob
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, LeakyReLU, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from pc_driver.TrainObject import TrainObject


class AIService:
    def __init__(self) -> None:
        self.model = Sequential([
            Input(shape=(40, 6)),
            LSTM(32, activation='tanh'),
            Dense(16),
            LeakyReLU(alpha=0.1),
            Dense(2, activation='softmax')
        ])
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        self.model.summary()

    def train_model(self):
        trainData: List[TrainObject] = []

        for filename in glob.glob("../data/*.json"):
            with open(filename, "r") as trainFile:
                data = json.load(trainFile)
                newTrainData: List[TrainObject] = [TrainObject(**item) for item in data]
                trainData.extend(newTrainData)

        if len(trainData) == 0:
            raise Exception("No training data found.")

        X = [to.sensor_data_to_2d_list() for to in trainData]
        y = [to.gesture for to in trainData]

        for seq in X:
            if len(seq) != 40:
                raise ValueError("Each gesture must have exactly 40 SensorData objects.")

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.int32)

        # One-hot encoding
        y = to_categorical(y, num_classes=2)

        # Normalizace dat na [-1,1]
        X = X / np.max(np.abs(X), axis=(0, 1))


        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )


        history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=16
        )


        plt.plot(history.history['accuracy'], label='train acc')
        plt.plot(history.history['val_accuracy'], label='val acc')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()


        model_num = len(glob.glob("../models/*.h5")) + 1
        self.model.save(f"../models/model_num_{model_num}.h5")
        print(f"Model saved as: ../models/model_num_{model_num}.h5")

    def load_model(self):
        model_names = glob.glob("../models/*.h5")
        if len(model_names) < 1:
            raise Exception("No models to load.")
        self.model = load_model(model_names[-1])
        print(f"Model loaded: {model_names[-1]}")
