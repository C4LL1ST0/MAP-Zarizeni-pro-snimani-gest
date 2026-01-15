from typing import List
import json
import glob
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, LeakyReLU, Input
from tensorflow.keras.optimizers import Adam
from textual.app import App
from .UiMessages import InfoMessage
from .Gesture import Gesture
from .SensorData import SensorData
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from .TrainObject import TrainObject
from sklearn.model_selection import train_test_split
import threading

class AIService:
    def __init__(self, ui: App) -> None:
        self.ui: App = ui
        self.gesture_length = 40

        self.model = Sequential([
            Input(shape=(self.gesture_length, 6)),
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

    def __train_model(self):
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
            if len(seq) != self.gesture_length:
                raise ValueError(f"Each gesture must have exactly {self.gesture_length} SensorData objects.")

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


        model_num = len(glob.glob("../models/*.h5")) + 1

        plt.plot(history.history['accuracy'], label='train acc')
        plt.plot(history.history['val_accuracy'], label='val acc')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.savefig(f"../figs/model_num_{model_num}")
        plt.close()

        self.model.save(f"../models/model_num_{model_num}.h5")
        self.ui.post_message(InfoMessage("Model trained successfully."))
        self.ui.post_message(InfoMessage(f"Model saved as: ../models/model_num_{model_num}.h5"))
    
    def train_model_other_thread(self):
        def tr_bulletproof():
            try:
                self.__train_model()
            except Exception as e:
                self.ui.call_from_thread(self.ui.post_message, InfoMessage(e.__str__()))

        threading.Thread(target=tr_bulletproof, daemon=True).start()

    def load_model(self):
        model_names = glob.glob("../models/*.h5")
        if len(model_names) < 1:
            raise Exception("No models to load.")
        self.model = load_model(model_names[-1])
        self.ui.post_message(InfoMessage(f"Model: {model_names[-1]} loaded."))

    def eval_gesture(self, sensor_data: List[SensorData]) -> Gesture:
        pass
