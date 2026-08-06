from sqlalchemy.orm import Session

from app.repositories.job_repository import JobRepository
from app.services.calendar_service import CalendarService


class CalendarSyncService:

    @staticmethod
    def sync_job(
        db: Session,
        job_id: int,
    ):
        job = JobRepository.get_by_id(
            db=db,
            job_id=job_id,
        )

        if job is None:
            raise ValueError("Job not found.")

        calendar = CalendarService()

        if job.calendar_synced and job.calendar_event_id:

            event = calendar.update_event(
                event_id=job.calendar_event_id,
                job=job,
            )

        else:

            event = calendar.create_event(job)

            JobRepository.mark_calendar_synced(
                db=db,
                job=job,
                event_id=event["id"],
            )

        return {
            "message": "Calendar synchronized successfully.",
            "event_id": event["id"],
            "event_link": event["htmlLink"],
            "calendar_synced": True,
        }

    @staticmethod
    def delete_job_event(
        db: Session,
        job_id: int,
    ):
        job = JobRepository.get_by_id(
            db=db,
            job_id=job_id,
        )

        if job is None:
            raise ValueError("Job not found.")

        if not job.calendar_synced or not job.calendar_event_id:
            raise ValueError("Calendar event not found.")

        calendar = CalendarService()

        calendar.delete_event(job.calendar_event_id)

        JobRepository.clear_calendar_sync(
            db=db,
            job=job,
        )

        return {
            "message": "Calendar event deleted successfully."
        }