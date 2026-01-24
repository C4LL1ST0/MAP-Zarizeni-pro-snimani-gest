from .Tui import Tui
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

if __name__ == "__main__":
    ui = Tui()
    ui.run()
