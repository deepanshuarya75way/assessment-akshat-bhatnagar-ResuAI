import logging
import os
import pickle
import time
from email.utils import parsedate_to_datetime
from ssl import SSLError

import httplib2
from google_auth_httplib2 import AuthorizedHttp
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from httplib2 import HttpLib2Error

from app.services.parser_service import EmailParser

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

TOKEN_PATH = "token.pickle"
CREDENTIALS_PATH = "credentials.json"
logger = logging.getLogger(__name__)


class GmailService:

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    HTTP_TIMEOUT_SECONDS = 30

    def __init__(self):

        self.creds = None
        self.service = None

        self.authenticate_gmail()

    def authenticate_gmail(self):

        if os.path.exists(TOKEN_PATH):

            with open(TOKEN_PATH, "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:

            if self.creds and self.creds.expired and self.creds.refresh_token:

                self.creds.refresh(Request())

            else:

                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH,
                    SCOPES,
                )

                self.creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(self.creds, token)

        http = httplib2.Http(
            timeout=self.HTTP_TIMEOUT_SECONDS
        )
        authed_http = AuthorizedHttp(
            self.creds,
            http=http,
        )

        self.service = build(
            "gmail",
            "v1",
            http=authed_http,
            cache_discovery=False,
        )

    def _execute_with_retry(
        self,
        request_factory,
        action: str,
    ):

        last_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return request_factory().execute()
            except (
                ConnectionAbortedError,
                ConnectionResetError,
                TimeoutError,
                OSError,
                SSLError,
                HttpLib2Error,
            ) as exc:
                last_error = exc
                logger.warning(
                    "Gmail %s failed on attempt %s/%s: %s",
                    action,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

                if attempt == self.MAX_RETRIES:
                    break

                self.authenticate_gmail()
                time.sleep(
                    self.RETRY_DELAY_SECONDS * attempt
                )

            except HttpError as exc:
                last_error = exc
                status_code = (
                    exc.resp.status
                    if exc.resp is not None
                    else None
                )

                if status_code not in {
                    429,
                    500,
                    502,
                    503,
                    504,
                }:
                    raise

                logger.warning(
                    "Gmail %s returned retryable HTTP %s on attempt %s/%s",
                    action,
                    status_code,
                    attempt,
                    self.MAX_RETRIES,
                )

                if attempt == self.MAX_RETRIES:
                    break

                self.authenticate_gmail()
                time.sleep(
                    self.RETRY_DELAY_SECONDS * attempt
                )

        raise last_error

    def list_messages(
        self,
        max_results: int = 10,
    ):

        results = self._execute_with_retry(
            lambda: (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results,
                )
            ),
            action="list_messages",
        )

        return results.get("messages", [])

    def get_message(
        self,
        message_id: str,
    ):

        return self._execute_with_retry(
            lambda: (
                self.service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",
                )
            ),
            action=f"get_message:{message_id}",
        )

    def read_latest_emails(self):

        messages = self.list_messages()

        emails = []

        for message in messages:

            gmail_message = self.get_message(message["id"])

            payload = gmail_message["payload"]

            headers = EmailParser.get_headers(payload)

            body = EmailParser.get_body(payload)

            links = EmailParser.extract_links(body)

            # --------------------------
            # Parse Gmail Date safely
            # --------------------------

            received_time = None

            date_header = headers.get("Date")

            if date_header:

                try:

                    # Remove "(UTC)" if present
                    date_header = date_header.replace(" (UTC)", "")

                    received_time = parsedate_to_datetime(date_header)

                except Exception:

                    received_time = None

            emails.append(
                {
                    "gmail_message_id": message["id"],
                    "subject": headers.get("Subject"),
                    "sender": headers.get("From"),
                    "received_time": received_time,
                    "body": body,
                    "links": links,
                }
            )

        return emails
