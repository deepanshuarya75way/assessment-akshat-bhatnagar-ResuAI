# from app.services.browser_auth import browser_auth

# browser_auth.login()
from app.auth.google_calendar import get_calendar_credentials

creds = get_calendar_credentials()

print(creds.valid)