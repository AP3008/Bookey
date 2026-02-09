from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Center, Middle, Container, Horizontal
from bookey.screens.calendar_ui import CalendarScreen


class MainMenu(Screen):
    #Initial Landing Page

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "calendar", "Calendar"),
        Binding("left", "app.focus_previous", "Previous", show=False),
        Binding("right", "app.focus_next", "Next", show=False)
    ]

    def compose(self):
        with Center():
            with Middle():
                with Container(id="main-card"):
                    yield Static(
                        " ██████╗  ██████╗  ██████╗ ██╗  ██╗███████╗██╗   ██╗\n"
                        " ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝╚██╗ ██╔╝\n"
                        " ██████╔╝██║   ██║██║   ██║█████╔╝ █████╗   ╚████╔╝ \n"
                        " ██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝    ╚██╔╝  \n"
                        " ██████╔╝╚██████╔╝╚██████╔╝██║  ██╗███████╗   ██║   \n"
                        " ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ",
                        id="logo",
                    )
                    yield Static(
                        "Your calendar, in the terminal.", id="tagline"
                    )
                    with Horizontal(id="buttons"):
                        yield Button("Calendar", id="btn-calendar", variant="primary")
                        yield Button("Exit", id="btn-exit")
                    yield Static("press 'q' to quit  |  'c' for calendar", id="hint")

    def on_mount(self):
        self.query_one("#btn-calendar").focus()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-calendar":
            self.action_calendar()
        elif event.button.id == "btn-exit":
            self.app.exit()

    def action_quit(self):
        self.app.exit()

    def action_calendar(self):
        self.app.push_screen(CalendarScreen())
