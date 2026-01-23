from .Tui import Tui

if __name__ == "__main__":
    ui = Tui()
    ui.run()

#
#receiver = Receiver(ui)
#
#dataFile = "nothing.json"
#gesture = Gesture.NOTHING
#receiver.capture_training_data(dataFile, gesture)
#
