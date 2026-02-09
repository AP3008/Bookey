from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from bookey.auth import login

class GoogleCalendar:
    def __init__(self):
        self.creds = login()

        #Creating objects for the calendars and tasks

        self.calendar = build('calendar', 'v3', credentials=self.creds)
        self.task = build('tasks', 'v1', credentials=self.creds)

    
    def getTasks(self):

        # Fetching raw tasks

        results = self.task.tasks().list(
            tasklist='@default',
            showCompleted=False
        ).execute()
        
        raw_tasks = results.get('items', [])
        
        # cleaned up version of the tasks being returned using list comprehension

        cleanTasks = [self._parse_task(t) for t in raw_tasks]
        return sorted(cleanTasks, key=lambda x: x['due'] if x['due'] else '9999-12-31')

    #Helper function to parse through the tasks into only necessary data

    def _parse_task(self, task):
        return {
            "id": task.get("id"),
            "title": task.get("title", "(No Title)"),
            "notes": task.get("notes", ""),  # Helpful for the 'Framer' or 'AWS' notes you have
            "due": task.get("due"),          # You might want to show this in the sidebar
            "status": task.get("status")
        }
    # Helper function to parse events

    def _parse_event(self, event):
        title = event.get('summary', '(No Title)')
        start_info = event.get('start', {})
        end_info = event.get('end', {})

        start = start_info.get('dateTime') or start_info.get('date')
        end = end_info.get('dateTime') or end_info.get('date')
        return {
            "id": event.get('id'),
            "title": title,
            "start": start,
            "end": end,
            "is_all_day": 'dateTime' not in start_info
        }


    def getCalendarSlots(self, focus_date: datetime, days):
        if days == 3:

            #If we are looks at 3 days the startdate and end date should be yesterday and tomorrow

            startDate = focus_date - timedelta(days=1)
            endDate = focus_date + timedelta(days=1)
        else:
            startDate = focus_date
            endDate = focus_date
        time_min = startDate.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        time_max = endDate.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        events = self.calendar.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
            ).execute()
        raw_events = events.get('items', [])

        # Putting data in dictionary for organization { "YYYY-MM-DD": [events] }

        organized_data = {}
        
        current = startDate
        while current <= endDate:
            date_str = current.strftime("%Y-%m-%d")
            organized_data[date_str] = []
            current += timedelta(days=1)

        # Sort each event into its day bucket

        for event in raw_events:

            # Google provides 'dateTime' (specific time) or 'date' (all-day event)

            start_raw = event['start'].get('dateTime') or event['start'].get('date')
            event_date = start_raw[:10] # Extract the YYYY-MM-DD part
            
            # adding events to the dates that we are looking into.

            if event_date in organized_data:
                organized_data[event_date].append(self._parse_event(event))

        return organized_data

if __name__ == "__main__":
    gc = GoogleCalendar()
    print('logged into google')
    today = datetime.now()
    print(f"Fetching 3-day view centered on: {today.date()}...")
    data = gc.getCalendarSlots(today, days=3)
    for date, events in data.items():
        print(f"\n--- {date} ---")
        if not events:
            print("  (No events found)")
        else:
            for ev in events:
                start_time = ev['start'][11:16] if not ev['is_all_day'] else "All Day"
                print(f"  [{start_time}] {ev['title']}")
    print("\n--- INCOMPLETE TASKS ---")
    tasks = gc.getTasks()
    for t in tasks:
        due_info = f" [Due: {t['due'][:10]}]" if t['due'] else ""
        print(f"  - {t['title']}{due_info}")
