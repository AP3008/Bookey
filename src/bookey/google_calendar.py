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
        results = self.task.tasks().list(tasklist='@default').execute()
        return results.get('items', [])

    # Helper function to parse events

    def _parse_events(self, event):
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
        
        # Initialize the dictionary with empty lists for the days in range

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
            
            if event_date in organized_data:
                organized_data[event_date].append(self._parse_event(event))

        return organized_data

        
