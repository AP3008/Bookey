import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If you change these scopes, you must delete token.json and log in again.

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

def login():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If the user has valid credentials and they are logging in again, we should just refresh the creds, and update our existing json with the new creds

        creds.refresh(Request()) 
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    
    # When the user is logging in through google, we need to write a token.json file so we can log them in without asking again. 

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


