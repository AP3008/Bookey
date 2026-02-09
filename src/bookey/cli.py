import sys
import tty
import termios
from datetime import datetime, timedelta


# ── Interactive Selector ────────────────────────────────────────


MAUVE = "\033[38;2;203;166;247m"
LAVENDER = "\033[38;2;180;190;254m"
GREEN = "\033[38;2;166;227;161m"
RED = "\033[38;2;243;139;168m"
DIM = "\033[38;2;108;112;134m"
TEXT = "\033[38;2;205;214;244m"
BOLD = "\033[1m"
RESET = "\033[0m"


def select_option(prompt, options):
    """Arrow-key interactive selector. Returns chosen index."""
    print(f"\n{MAUVE}?{RESET} {BOLD}{prompt}{RESET}")
    selected = 0
    count = len(options)

    def render():
        for i, opt in enumerate(options):
            if i == selected:
                print(f"\033[K  {MAUVE}❯ {i + 1}. {opt}{RESET}")
            else:
                print(f"\033[K    {DIM}{i + 1}. {opt}{RESET}")

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    render()
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == "\r":
                break
            elif ch == "\x1b":
                sys.stdin.read(1)  # skip [
                arrow = sys.stdin.read(1)
                if arrow == "A" and selected > 0:
                    selected -= 1
                elif arrow == "B" and selected < count - 1:
                    selected += 1
            elif ch.isdigit():
                idx = int(ch) - 1
                if 0 <= idx < count:
                    selected = idx
                    break
            elif ch == "\x03":  # Ctrl+C
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
                print(f"\n{RESET}")
                sys.exit(0)
            # Redraw
            sys.stdout.write(f"\033[{count}A")
            sys.stdout.flush()
            render()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print()
    return selected


def ask(prompt, required=True, hint=""):
    """Simple input prompt with Catppuccin styling."""
    suffix = f" {DIM}{hint}{RESET}" if hint else ""
    while True:
        val = input(f"{MAUVE}?{RESET} {BOLD}{prompt}{RESET}{suffix}: ")
        if val or not required:
            return val
        print(f"  {RED}This field is required.{RESET}")


# ── Add Flow ────────────────────────────────────────────────────


def cli_add(gc):
    choice = select_option("What would you like to add?", ["Event", "Task"])

    if choice == 0:
        _add_event(gc)
    else:
        _add_task(gc)


def _add_event(gc):
    name = ask("Name")
    date_str = ask("Date (dd/mm/yyyy)")
    time_str = ask("Start time (hh:mm, or 'a' for all day)")
    is_all_day = time_str.lower() == "a"

    if not is_all_day:
        end_str = ask("End time (hh:mm)")
    desc = ask("Description", required=False)

    # Parse date
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        print(f"  {RED}Invalid date format. Use dd/mm/yyyy{RESET}")
        return

    date_iso = dt.strftime("%Y-%m-%d")

    if is_all_day:
        # All-day events use date-only format
        gc.add_calendar(name, date_iso, date_iso, desc or "")
        print(f"\n  {GREEN}✓{RESET} Event {BOLD}\"{name}\"{RESET} added for {dt.strftime('%b %d, %Y')} (all day)")
    else:
        start_iso = f"{date_iso}T{time_str}:00"
        end_iso = f"{date_iso}T{end_str}:00"
        gc.add_calendar(name, start_iso, end_iso, desc or "")
        print(f"\n  {GREEN}✓{RESET} Event {BOLD}\"{name}\"{RESET} added for {dt.strftime('%b %d, %Y')} {time_str}-{end_str}")


def _add_task(gc):
    name = ask("Name")
    date_str = ask("Date (dd/mm/yyyy)", required=False, hint="[enter to skip]")
    desc = ask("Description", required=False)

    due = None
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            due = dt.strftime("%Y-%m-%dT00:00:00.000Z")
        except ValueError:
            print(f"  {RED}Invalid date format. Use dd/mm/yyyy{RESET}")
            return

    gc.add_task(name, desc or "", due)

    if due:
        print(f"\n  {GREEN}✓{RESET} Task {BOLD}\"{name}\"{RESET} added for {dt.strftime('%b %d, %Y')}")
    else:
        print(f"\n  {GREEN}✓{RESET} Task {BOLD}\"{name}\"{RESET} added")


# ── Delete Flow ─────────────────────────────────────────────────


def cli_delete(gc):
    choice = select_option(
        "What would you like to remove?", ["Event", "Task"]
    )

    if choice == 0:
        _delete_event(gc)
    else:
        _complete_task(gc)


def _delete_event(gc):
    # Fetch events for the next 7 days
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    all_events = []
    for i in range(7):
        day = today + timedelta(days=i)
        slots = gc.getCalendarSlots(day, 1)
        for date_str, events in slots.items():
            for event in events:
                event["_date_str"] = date_str
                all_events.append(event)

    if not all_events:
        print(f"\n  {DIM}No events in the next 7 days.{RESET}")
        return

    print(f"\n  {LAVENDER}Events for the next 7 days:{RESET}")
    labels = []
    for event in all_events:
        dt = datetime.strptime(event["_date_str"], "%Y-%m-%d")
        day_label = dt.strftime("%a, %b %d")
        if event["is_all_day"]:
            labels.append(f"{day_label} | {event['title']} (all day)")
        else:
            start_time = event["start"][11:16] if len(event["start"]) > 11 else ""
            labels.append(f"{day_label} | {event['title']} ({start_time})")

    idx = select_option("Select event to delete:", labels)
    event = all_events[idx]
    gc.delete_calendar(event["id"])
    print(f"  {GREEN}✓{RESET} Deleted {BOLD}\"{event['title']}\"{RESET}")


def _complete_task(gc):
    tasks = gc.getTasks()

    if not tasks:
        print(f"\n  {DIM}No tasks to complete.{RESET}")
        return

    print(f"\n  {LAVENDER}Your tasks:{RESET}")
    labels = []
    for task in tasks:
        if task["due"]:
            dt = datetime.strptime(task["due"][:10], "%Y-%m-%d")
            labels.append(f"{dt.strftime('%b %d')} | {task['title']}")
        else:
            labels.append(task["title"])

    idx = select_option("Select task to complete:", labels)
    task = tasks[idx]
    gc.complete_task(task["id"])
    print(f"  {GREEN}✓{RESET} Completed {BOLD}\"{task['title']}\"{RESET}")
