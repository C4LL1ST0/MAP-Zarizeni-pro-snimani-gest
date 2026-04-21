from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Log, Input

from .Gesture import gesture_dict
from .AIService import AIService
from .Receiver import Receiver
from .UiMessages import GestureMessage, SensorDataMessage, InfoMessage
from textual.worker import WorkerFailed


class Tui(App):
    CSS = """
    #data_log_text {
        border: solid yellow;
    }
    #message_text {
        border: solid yellow;
    }
     #gesture_text {
        border: solid yellow;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "start_receiver", "start receiving", show=True, priority=True),
        Binding("ctrl+t", "train_model", "train model", show=True, priority=True),
        Binding("ctrl+d", "collect_train_data", "collect train data", show=True, priority=True)
    ]

    gesture = reactive(None)
    filename = reactive("")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Log(id="data_log_text")
            with Vertical(id="right_side"):
                yield Log(id="message_text")
                yield Input(id="gesture_text", placeholder="gesture")
        yield Footer()

    async def on_mount(self) -> None:
        self.ai_service = AIService(self)
        self.receiver = Receiver(self, self.ai_service)

        try:
            self.ai_service.load_model()
            self.post_message(InfoMessage("Model loaded successfully."))

        except Exception as e:
            self.post_message(InfoMessage(str(e)))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "gesture_text":
            try:
                self.gesture = gesture_dict[event.input.value]
                self.filename = event.input.value + ".json"
                self.post_message(InfoMessage("Gesture selected."))
            except KeyError as ke:
                self.post_message(InfoMessage("Specify valid gesture."))

    def action_start_receiver(self):
        self.post_message(InfoMessage("Starting receiver..."))
        self.receiver.start_receiving()


    def action_train_model(self):
        self.post_message(InfoMessage("Training model..."))
        self.ai_service.train_model_other_thread()

    def action_collect_train_data(self):
        if self.filename == "" or self.gesture is None:
            self.post_message(InfoMessage("Specify valid filename and gesture."))
            return

        self.post_message(InfoMessage("Colecting train data..."))
        self.receiver.capture_data_thread(self.filename, self.gesture)

    async def on_sensor_data_message(self, message: SensorDataMessage) -> None:
        log = self.query_one("#data_log_text", Log)
        d = message.data

        log.write(
            f"AcX={d.AcX}, AcY={d.AcY}, AcZ={d.AcZ} | "
            f"GyX={d.GyX}, GyY={d.GyY}, GyZ={d.GyZ} \n"
        )

    async def on_info_message(self, message: InfoMessage) -> None:
        log = self.query_one("#message_text", Log)
        log.write(message.msg + "\n")

    async def on_gesture_message(self, message: GestureMessage):
        log = self.query_one("#message_text", Log)
        log.write(str(message.gesture) + "\n")

    async def on_worker_failed(self, event: WorkerFailed):
        self.post_message(InfoMessage(str(event.error)))
