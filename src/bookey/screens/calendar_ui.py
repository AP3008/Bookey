from datetime import datetime, timedelta
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.widget import Widget
from textual.widgets import Static, Button, Input, Select
from textual.containers import Container, Horizontal, ScrollableContainer


# ── Helper Widgets ──────────────────────────────────────────────


class TimeSlot(Static):
    """A single 30-minute time slot in the day grid."""

    def __init__(self, time_label: str, event: dict | None, is_start: bool):
        self.time_label = time_label
        self.event_data = event
        self.event_id = event["id"] if event else None

        if event and is_start:
            display = f" {time_label} \u2502 {event['title']}"
            classes = "time-slot occupied event-start"
        elif event:
            display = f" {time_label} \u2502   \u2026"
            classes = "time-slot occupied event-cont"
        else:
            display = f" {time_label} \u2502"
            classes = "time-slot"

        super().__init__(display, classes=classes)


class TaskItem(Static):
    """A single task row in the tasks panel."""

    def __init__(self, task: dict):
        self.task_id = task["id"]
        due = task["due"][:10] if task["due"] else "no date"
        display = f" {task['title']}  \u2502  {due}"
        super().__init__(display, classes="task-item")


class DayColumn(Widget):
    """A single day column with header and scrollable time grid."""

    def __init__(self, date_str: str, events: list[dict], column_index: int):
        super().__init__(id=f"day-col-{column_index}")
        self.date_str = date_str
        self.events = events
        self.column_index = column_index

    def compose(self) -> ComposeResult:
        dt = datetime.strptime(self.date_str, "%Y-%m-%d")
        label = dt.strftime("%a %b %d").upper()
        today = datetime.now().strftime("%Y-%m-%d")
        if self.date_str == today:
            label += "  (TODAY)"

        yield Static(label, classes="day-header")

        all_day = [e for e in self.events if e["is_all_day"]]
        if all_day:
            text = " \u2502 ".join(e["title"] for e in all_day)
            yield Static(f" {text}", classes="all-day-bar")

        with ScrollableContainer(classes="time-grid"):
            for hour in range(24):
                for minute in (0, 30):
                    time_label = f"{hour:02d}:{minute:02d}"
                    event, is_start = self._find_event_for_slot(hour, minute)
                    yield TimeSlot(time_label, event, is_start)

    def _find_event_for_slot(
        self, hour: int, minute: int
    ) -> tuple[dict | None, bool]:
        for event in self.events:
            if event["is_all_day"]:
                continue
            start_dt = datetime.fromisoformat(event["start"])
            end_dt = datetime.fromisoformat(event["end"])
            # Build slot boundaries using the day's date
            day_date = datetime.strptime(self.date_str, "%Y-%m-%d")
            slot_start = day_date.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0,
                tzinfo=start_dt.tzinfo,
            )
            slot_end = slot_start + timedelta(minutes=30)
            if start_dt < slot_end and end_dt > slot_start:
                is_start = start_dt.hour == hour and (
                    start_dt.minute >= minute and start_dt.minute < minute + 30
                )
                return event, is_start
        return None, False


# ── Modals ──────────────────────────────────────────────────────


class AddModal(ModalScreen):
    """Modal for adding a new event or task."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Container(id="add-modal-card"):
            yield Static("Add New...", id="add-modal-title")
            yield Select(
                [("Event", "event"), ("Task", "task")],
                id="add-type-select",
                value="event",
            )
            with Container(id="event-fields"):
                yield Input(placeholder="Event title", id="add-title")
                yield Input(placeholder="Start time (HH:MM)", id="add-start")
                yield Input(placeholder="End time (HH:MM)", id="add-end")
                yield Input(placeholder="Details (optional)", id="add-details")
            with Container(id="task-fields"):
                yield Input(placeholder="Task title", id="add-task-title")
                yield Input(placeholder="Notes (optional)", id="add-task-notes")
                yield Input(
                    placeholder="Due date YYYY-MM-DD (optional)",
                    id="add-task-due",
                )
            with Horizontal(id="add-modal-buttons"):
                yield Button("Save", id="btn-add-save", variant="primary")
                yield Button("Cancel", id="btn-add-cancel")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value == "event":
            self.query_one("#event-fields").display = True
            self.query_one("#task-fields").display = False
        else:
            self.query_one("#event-fields").display = False
            self.query_one("#task-fields").display = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-add-save":
            select_val = self.query_one("#add-type-select", Select).value
            if select_val == "event":
                result = {
                    "type": "event",
                    "title": self.query_one("#add-title", Input).value,
                    "start": self.query_one("#add-start", Input).value,
                    "end": self.query_one("#add-end", Input).value,
                    "details": self.query_one("#add-details", Input).value,
                }
            else:
                result = {
                    "type": "task",
                    "title": self.query_one("#add-task-title", Input).value,
                    "notes": self.query_one("#add-task-notes", Input).value,
                    "due": self.query_one("#add-task-due", Input).value,
                }
            self.dismiss(result)

    def action_cancel(self) -> None:
        self.dismiss(None)


class DeleteModal(ModalScreen):
    """Modal for selecting an event to delete or task to complete."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, events: list[dict], tasks: list[dict]):
        super().__init__()
        self.events = events
        self.tasks = tasks
        self._id_map: dict[int, tuple[str, str]] = {}

    def compose(self) -> ComposeResult:
        with Container(id="delete-modal-card"):
            yield Static("Delete Event / Complete Task", id="delete-modal-title")
            with ScrollableContainer(id="delete-list"):
                idx = 0
                for event in self.events:
                    start_short = event["start"][:16] if event["start"] else ""
                    self._id_map[idx] = ("delete_event", event["id"])
                    yield Button(
                        f"[Event] {event['title']}  ({start_short})",
                        id=f"del-{idx}",
                        classes="delete-item-btn",
                    )
                    idx += 1
                for task in self.tasks:
                    self._id_map[idx] = ("complete_task", task["id"])
                    yield Button(
                        f"[Task] {task['title']}",
                        id=f"del-{idx}",
                        classes="delete-item-btn",
                    )
                    idx += 1
                if idx == 0:
                    yield Static("No events or tasks to manage.", classes="empty-list")
            yield Button("Cancel", id="btn-delete-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-delete-cancel":
            self.dismiss(None)
        elif btn_id.startswith("del-"):
            idx = int(btn_id[4:])
            action, real_id = self._id_map[idx]
            self.dismiss({"action": action, "id": real_id})

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Main Calendar Screen ────────────────────────────────────────


class CalendarScreen(Screen):
    """The calendar interface with day view, tasks panel, and CRUD."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", priority=True),
        Binding("1", "view_1day", "1-Day", priority=True),
        Binding("3", "view_3day", "3-Day", priority=True),
        Binding("a", "add_item", "Add", priority=True),
        Binding("d", "delete_item", "Delete", priority=True),
    ]

    view_mode: reactive[int] = reactive(3)

    def __init__(self, gc):
        super().__init__()
        self.gc = gc
        self.focus_date: datetime = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self._calendar_data: dict[str, list[dict]] = {}
        self._current_events: list[dict] = []
        self._current_tasks: list[dict] = []
        self._load_data()

    def on_mount(self) -> None:
        self.call_after_refresh(self._scroll_to_now)

    def _load_data(self) -> None:
        self._calendar_data = self.gc.getCalendarSlots(
            self.focus_date, self.view_mode
        )
        self._current_tasks = self.gc.getTasks()
        self._current_events = []
        for day_events in self._calendar_data.values():
            self._current_events.extend(day_events)

    def compose(self) -> ComposeResult:
        mode_label = "3-Day View" if self.view_mode == 3 else "1-Day View"
        date_label = self.focus_date.strftime("%b %d, %Y")
        yield Static(f"  {mode_label}  \u2502  {date_label}", id="cal-header")

        with Horizontal(id="cal-body"):
            with Horizontal(id="day-columns"):
                for i, (date_str, events) in enumerate(
                    self._calendar_data.items()
                ):
                    yield DayColumn(date_str, events, column_index=i)

            with Container(id="tasks-panel"):
                yield Static(" Tasks", id="tasks-header")
                with ScrollableContainer(id="tasks-list"):
                    if self._current_tasks:
                        for task in self._current_tasks:
                            yield TaskItem(task)
                    else:
                        yield Static(" No tasks", classes="empty-list")

        yield Static(
            " [a] Add  [d] Delete/Complete  [1] 1-Day  [3] 3-Day  [esc] Back",
            id="cal-footer",
        )

    def _scroll_to_now(self) -> None:
        now = datetime.now()
        slot_index = now.hour * 2 + (1 if now.minute >= 30 else 0)
        for grid in self.query(".time-grid"):
            grid.scroll_to(y=max(0, slot_index - 2), animate=False)

    def watch_view_mode(self, new_mode: int) -> None:
        if hasattr(self, "_calendar_data") and self._calendar_data:
            self._load_data()
            self.recompose()
            self.call_after_refresh(self._scroll_to_now)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_view_1day(self) -> None:
        self.view_mode = 1

    def action_view_3day(self) -> None:
        self.view_mode = 3

    def action_add_item(self) -> None:
        self.app.push_screen(AddModal(), callback=self._on_add_complete)

    def _on_add_complete(self, result: dict | None) -> None:
        if result is None:
            return
        if result["type"] == "event":
            date_str = self.focus_date.strftime("%Y-%m-%d")
            start_iso = f"{date_str}T{result['start']}:00"
            end_iso = f"{date_str}T{result['end']}:00"
            self.gc.add_calendar(
                result["title"], start_iso, end_iso, result.get("details", "")
            )
        elif result["type"] == "task":
            due = result.get("due") or None
            self.gc.add_task(
                result["title"], result.get("notes", ""), due
            )
        self._load_data()
        self.recompose()
        self.call_after_refresh(self._scroll_to_now)

    def action_delete_item(self) -> None:
        self.app.push_screen(
            DeleteModal(self._current_events, self._current_tasks),
            callback=self._on_delete_complete,
        )

    def _on_delete_complete(self, result: dict | None) -> None:
        if result is None:
            return
        if result["action"] == "delete_event":
            self.gc.delete_calendar(result["id"])
        elif result["action"] == "complete_task":
            self.gc.complete_task(result["id"])
        self._load_data()
        self.recompose()
        self.call_after_refresh(self._scroll_to_now)
