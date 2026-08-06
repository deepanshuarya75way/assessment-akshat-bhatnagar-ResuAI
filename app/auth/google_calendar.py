from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_PATH = (
    BASE_DIR
    / "credentials"
    / "credentials2.json"
)

TOKEN_PATH = (
    BASE_DIR
    / "tokens"
    / "calendar_token.json"
)


def get_calendar_credentials():

    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_PATH),
            SCOPES,
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        TOKEN_PATH.parent.mkdir(
            exist_ok=True,
            parents=True,
        )

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds