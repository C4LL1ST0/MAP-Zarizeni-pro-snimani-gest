from typing import List
import json
import glob
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, LeakyReLU, Input
from tensorflow.keras.optimizers import Adam
from textual.app import App
from .UiMessages import InfoMessage, GestureMessage
from .Gesture import Gesture
from .SensorData import SensorData
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from .TrainObject import TrainObject
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import threading

class AIService:
    def __init__(self, ui: App) -> None:
        self.ui: App = ui
        self.norm = None
        self.gesture_length = 45
        
        self.model = Sequential([
            Input(shape=(45, 6)),
            LSTM(16, activation='tanh'),
            Dense(8),
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

        X, y = shuffle(X, y, random_state=42)

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.norm = np.max(np.abs(X_train), axis=(0, 1))
        X_train = X_train / self.norm
        X_val = X_val / self.norm


        history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=10,
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

        np.save(f"../models/norm_num_{model_num}.npy", self.norm)
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
        norm_names = glob.glob("../models/*.npy")
        if len(model_names) < 1 or len(norm_names) < 1:
            raise Exception("No models to load.")
        self.model = load_model(model_names[-1])
        self.norm = np.load(norm_names[-1])
        self.ui.post_message(InfoMessage(f"Model: {model_names[-1]} loaded."))

    def eval_gesture(self, sensor_data: List[SensorData]) -> None:
        if(self.model is None or self.norm is None):
            self.ui.post_message(InfoMessage("no model"))
            raise Exception("Cannot eval, no model loaded.")

        X = np.array([sd.to_array() for sd in sensor_data], dtype=np.float32)
        X = np.expand_dims(X, axis=0)
        X = X / self.norm
        probs = self.model.predict(X, verbose=0)[0]

        THRESHOLD = 0.8
        if np.max(probs) < THRESHOLD:
            return

        class_index = int(np.argmax(probs))
        gesture = Gesture(class_index)
        self.ui.post_message(GestureMessage(gesture))
