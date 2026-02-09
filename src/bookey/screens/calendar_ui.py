from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Center, Middle


class CalendarScreen(Screen):
    # Calendar Screen

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("left", "app.focus_previous", "Previous", show=False),
        Binding("right", "app.focus_next", "Next", show=False),
        Binding("1", "", ""), # Shows 1 Day View 
        Binding("3", "", "") # Shows 3 Day View 
    ]

    def compose(self):
        with Center():
            with Middle():
                yield Static("Calendar coming soon...", id="placeholder")

    def action_go_back(self):
        self.app.pop_screen()
