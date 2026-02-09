import argparse

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
    parser = argparse.ArgumentParser(description="Bookey - Your calendar, in the terminal.")
    parser.add_argument("-a", action="store_true", help="Add an event or task")
    parser.add_argument("-d", action="store_true", help="Delete event or complete task")
    args = parser.parse_args()

    if args.a:
        from bookey.cli import cli_add
        gc = GoogleCalendar()
        cli_add(gc)
    elif args.d:
        from bookey.cli import cli_delete
        gc = GoogleCalendar()
        cli_delete(gc)
    else:
        app = BookeyApp()
        app.run()


if __name__ == "__main__":
    main()
