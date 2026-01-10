from typing import List
import json
from pc_driver.TrainObject import TrainObject
import glob
from pc_driver.SensorData import SensorData
from pc_driver.Gesture import Gesture
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, LeakyReLU, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model


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

        for filename in glob.glob("../data/"):
            trainFile = open("../data/" + filename, "r")
            data = json.load(trainFile)
            newTrainData: List[TrainObject] = [TrainObject(**item) for item in data]
            trainFile.close()

            trainData.extend(newTrainData)


        X_train: List[SensorData] = map(lambda to: to.sensorData, trainData)
        y_train: List[Gesture] = map(lambda to: to.gesture, trainData)

        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
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

        model_num = len(glob.glob("../models/")) + 1
        self.model.save("../models/model_num_" + str(model_num) + ".h5")

    def load_model(self):
        model_names = glob.glob("../models/")

        if (len(model_names) < 1):
            raise Exception("No models to load.")

        self.model = load_model(model_names[len(model_names-1)]) # s trochou stesti model s nejvysim cislem
