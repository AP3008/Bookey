import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If you change these scopes, you must delete token.json and log in again.

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

def login():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_files("token.json", SCOPES)
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

    # When the user is logging in through google, we need to write a token.json file so we can log them in without asking again. 

        with open("token.json") as token_json:
            token_json.write(creds.to_json())

if __name__ == "__main__":
    login()
    print('Logged in successfully')
