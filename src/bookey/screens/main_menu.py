from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, ListItem, ListView
from textual.containers import Center, Middle

class MainMenu(Screen):
    """The initial landing page of Bookey."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Static(
                    " ██████╗  ██████╗  ██████╗ ██╗  ██╗███████╗██╗   ██╗\n"
                    " ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝╚██╗ ██╔╝\n"
                    " ██████╔╝██║   ██║██║   ██║█████╔╝ █████╗   ╚████╔╝ \n"
                    " ██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝    ╚██╔╝  \n"
                    " ██████╔╝╚██████╔╝╚██████╔╝██║  ██╗███████╗   ██║   \n"
                    " ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ",
                    id="logo"
                )
                yield Static("Welcome, Adam. Select a module:", id="welcome")
                
                with ListView(id="menu-options"):
                    yield ListItem(Static("Go to Calendar Interface"), id="nav-calendar")
                    yield ListItem(Static("CLI Tools & Utilities"), id="nav-tools")
                    yield ListItem(Static("Settings"), id="nav-settings")
                    yield ListItem(Static("Exit"), id="nav-exit")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected):
        #Menu Navigation
        if event.list_item.id == "nav-calendar":
            # We will handle the switch in the App level or 
            # by importing the Calendar screen here.
            from bookey.screens.calendar import CalendarScreen
            self.app.push_screen(CalendarScreen())
        elif event.list_item.id == "nav-exit":
            self.app.exit()
