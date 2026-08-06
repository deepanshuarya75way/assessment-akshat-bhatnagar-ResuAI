from datetime import timedelta

from dateutil import parser
from googleapiclient.discovery import build

from app.auth.google_calendar import get_calendar_credentials
from app.models.job import Job


class CalendarService:

    def __init__(self):
        credentials = get_calendar_credentials()

        self.service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )

        self.calendar_id = "primary"

    def create_event(self, job: Job) -> dict:

        if not job.application_deadline:
            raise ValueError("Application deadline not found.")

        deadline = parser.parse(
            job.application_deadline.replace("·", " "),
            fuzzy=True,
        )

        # Make the event one hour long
        start_time = deadline.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        event = {
            "summary": f"📌 Apply: {job.role} @ {job.company}",
            "location": job.location or "",
            "description": (
                f"Company: {job.company}\n"
                f"Role: {job.role}\n"
                f"Job Type: {job.job_type}\n"
                f"CTC: {job.ctc}\n"
                f"Stipend: {job.stipend}\n"
                f"Minimum CGPA: {job.minimum_cgpa}\n"
                f"Batch: {job.batch}\n\n"
                f"Apply URL:\n{job.apply_url}\n\n"
                f"Skills Required:\n"
                f"{', '.join(job.skills_required or [])}"
            ),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": "popup",
                        "minutes": 10080,   # 7 days
                    },
                    {
                        "method": "popup",
                        "minutes": 2880,    # 2 days
                    },
                    {
                        "method": "popup",
                        "minutes": 1440,    # 1 day
                    },
                    {
                        "method": "popup",
                        "minutes": 120,     # 2 hours
                    },
                ],
            },
        }

        created_event = (
            self.service.events()
            .insert(
                calendarId=self.calendar_id,
                body=event,
            )
            .execute()
        )

        return created_event

    def get_event(self, event_id: str) -> dict:

        return (
            self.service.events()
            .get(
                calendarId=self.calendar_id,
                eventId=event_id,
            )
            .execute()
        )

    def update_event(
        self,
        event_id: str,
        job: Job,
    ) -> dict:

        event = self.get_event(event_id)

        deadline = parser.parse(
            job.application_deadline.replace("·", " "),
            fuzzy=True,
        )

        start_time = deadline.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )

        end_time = start_time + timedelta(hours=1)

        event["summary"] = f"📌 Apply: {job.role} @ {job.company}"

        event["location"] = job.location or ""

        event["description"] = (
            f"Company: {job.company}\n"
            f"Role: {job.role}\n"
            f"Job Type: {job.job_type}\n"
            f"CTC: {job.ctc}\n"
            f"Stipend: {job.stipend}\n"
            f"Minimum CGPA: {job.minimum_cgpa}\n"
            f"Batch: {job.batch}\n\n"
            f"Apply URL:\n{job.apply_url}\n\n"
            f"Skills Required:\n"
            f"{', '.join(job.skills_required or [])}"
        )

        event["start"] = {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        }

        event["end"] = {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        }

        updated = (
            self.service.events()
            .update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
            )
            .execute()
        )

        return updated

    def delete_event(self, event_id: str) -> bool:

        (
            self.service.events()
            .delete(
                calendarId=self.calendar_id,
                eventId=event_id,
            )
            .execute()
        )

        return True