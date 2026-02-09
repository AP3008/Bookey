import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If you change these scopes, you must delete token.json and log in again.

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "bookey")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
CREDS_PATH = os.path.join(CONFIG_DIR, "credentials.json")

def login():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If the user has valid credentials and they are logging in again, we should just refresh the creds, and update our existing json with the new creds

        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

    # When the user is logging in through google, we need to write a token.json file so we can log them in without asking again.

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


