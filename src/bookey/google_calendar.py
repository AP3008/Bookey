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
            "notes": task.get("notes", ""),  
            "due": task.get("due"),         
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

    def add_calendar(self, summary, start_time, end_time, description=""):
        event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/Toronto'},
        'end': {'dateTime': end_time, 'timeZone': 'America/Toronto'},
        }
        return self.calendar.events().insert(calendarId="primary", body=event).execute()

    def delete_calendar(self, eventID):
        return self.calendar.events().delete(calendarId='primary', eventId=eventID).execute()

    def add_task(self, title, notes, due=None):
        t_body = {
            'title': title,
            'notes': notes
        }
        if due:
            t_body['due'] = due
        return self.task.tasks().insert(tasklist='@default', body=t_body).execute()

    def complete_task(self, taskID):
        t_body = {
            'status': 'completed'
        }
        return self.task.tasks().patch(
            tasklist='@default',
            task=taskID,
            body=t_body
        ).execute()

