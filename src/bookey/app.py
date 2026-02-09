from textual.app import App
from bookey.google_calendar import GoogleCalendar
from bookey.screens.main_menu import MainMenu


class BookeyApp(App):
    CSS_PATH = "style.tcss"
    TITLE = "Bookey"

    def on_mount(self) -> None:
        self.gc = GoogleCalendar()
        self.push_screen(MainMenu())


def main():
    app = BookeyApp()
    app.run()


if __name__ == "__main__":
    main()
