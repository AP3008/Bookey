from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from bookey.auth import login

class GoogleCalendar:
    def __init__(self):
        self.creds = login()

        #Creating objects for the calendars and tasks

        self.calendar = build('calendar', 'v3', credentials=creds)
        self.calendar = build('tasks', 'v1', credentials=creds)

