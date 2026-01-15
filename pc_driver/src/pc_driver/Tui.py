from enum import Enum, auto
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Log, Input
from .AIService import AIService
from .Receiver import Receiver
from .UiMessages import SensorDataMessage, InfoMessage
from textual.reactive import reactive
from textual.worker import WorkerFailed


class WaitingFor(Enum):
    NONE = auto()
    TRAIN_CONFIRM = auto()


class Tui(App):

    CSS = """
    #data_log_text {
        border: solid yellow;
    }
    #message_text {
        border: solid yellow;
    }
    #input {
        border: solid yellow;
    }
    """

    waiting_for = reactive(WaitingFor.NONE)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Log(id="data_log_text")
            with Vertical():
                yield Log(id="message_text")
                yield Input(id="input")

    async def on_mount(self) -> None:
        input_widget = self.query_one("#input", Input)
        input_widget.disabled = True

        self.ai_service = AIService(self)
        self.receiver = Receiver(self, self.ai_service)

        try:
            self.ai_service.load_model()
            self.post_message(InfoMessage("Model loaded successfully."))
            await self.start_application_flow()

        except Exception as e:
            self.post_message(InfoMessage(str(e)))
            self.ask_train_question()


    async def start_application_flow(self) -> None:
        self.post_message(InfoMessage("Starting receiver..."))
        self.receiver.start_receiving()

    def ask_train_question(self) -> None:
        self.post_message(InfoMessage("Do you want to train a model? (y/n)"))

        self.waiting_for = WaitingFor.TRAIN_CONFIRM

        input_widget = self.query_one("#input", Input)
        input_widget.disabled = False
        input_widget.focus()


    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text: str = event.value
        self.post_message(InfoMessage(text))
        event.input.value = ""

        if self.waiting_for == WaitingFor.TRAIN_CONFIRM:
            await self.handle_train_confirm(text)
            return

        self.post_message(InfoMessage(f"Unknown command: {text}"))

    async def handle_train_confirm(self, answer: str) -> None:
        input_text = self.query_one("#input", Input)

        if answer == "y":
            self.post_message(InfoMessage("Training model..."))
            self.waiting_for = WaitingFor.NONE
            input_text.disabled = True

            self.ai_service.train_model_other_thread()

            await self.start_application_flow()

        elif answer == "n":
            self.post_message(InfoMessage("Model training skipped."))
            self.waiting_for = WaitingFor.NONE
            input_text.disabled = True

            await self.start_application_flow()

        else:
            self.post_message(InfoMessage("Please answer y or n."))
            input_text.focus()


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

    async def on_worker_failed(self, event: WorkerFailed):
        self.post_message(InfoMessage(str(event.error)))
