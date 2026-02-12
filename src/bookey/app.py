import os
import argparse

from bookey.google_calendar import GoogleCalendar
from bookey.auth import TOKEN_PATH
from bookey.cli import select_option, cli_add, cli_delete, cli_list, MAUVE, GREEN, RED, BOLD, RESET, DIM


LOGO = f"""{MAUVE}{BOLD}
  ____              _
 | __ )  ___   ___ | | _____ _   _
 |  _ \\ / _ \\ / _ \\| |/ / _ \\ | | |
 | |_) | (_) | (_) |   <  __/ |_| |
 |____/ \\___/ \\___/|_|\\_\\___|\\__, |
                             |___/
{RESET}{DIM}  Your calendar, in the terminal.{RESET}
"""


def change_login():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        print(f"  {GREEN}Logged out. Logging in with new account...{RESET}\n")
    else:
        print(f"  {DIM}No existing login found. Logging in...{RESET}\n")
    GoogleCalendar()
    print(f"\n  {GREEN}Login successful!{RESET}")


def main_menu():
    print(LOGO)
    gc = GoogleCalendar()

    while True:
        choice = select_option("What would you like to do?", [
            "Add event or task",
            "Delete event / complete task",
            "List events or tasks",
            "Change login",
            "Exit",
        ])

        if choice == 0:
            cli_add(gc)
        elif choice == 1:
            cli_delete(gc)
        elif choice == 2:
            cli_list(gc)
        elif choice == 3:
            change_login()
            gc = GoogleCalendar()
        elif choice == 4:
            print(f"\n  {DIM}Goodbye!{RESET}\n")
            break

        print()


def main():
    parser = argparse.ArgumentParser(description="Bookey - Your calendar, in the terminal.")
    parser.add_argument("-a", action="store_true", help="Add an event or task")
    parser.add_argument("-d", action="store_true", help="Delete event or complete task")
    parser.add_argument("-l", action="store_true", help="List events or tasks")
    parser.add_argument("--change-login", action="store_true", help="Switch Google account")
    args = parser.parse_args()

    if args.a:
        gc = GoogleCalendar()
        cli_add(gc)
    elif args.d:
        gc = GoogleCalendar()
        cli_delete(gc)
    elif args.l:
        gc = GoogleCalendar()
        cli_list(gc)
    elif args.change_login:
        change_login()
    else:
        main_menu()


if __name__ == "__main__":
    main()
