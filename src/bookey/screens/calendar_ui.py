from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Center, Middle


class CalendarScreen(Screen):
    """Placeholder for the calendar interface."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Static("Calendar coming soon...", id="placeholder")

    def action_go_back(self) -> None:
        self.app.pop_screen()
