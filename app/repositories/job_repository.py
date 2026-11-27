from sqlalchemy.orm import Session
from app.models.job import Job

class JobRepository:

    @staticmethod
    def update(
        db: Session,
        job: Job,
        job_data: dict,
    ):
        for field, value in job_data.items():
            setattr(job, field, value)

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def create(
        db: Session,
        job_data: dict,
        email_id: int,
    ):
        job = Job(
            email_id=email_id,
            **job_data,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_by_email(
        db: Session,
        email_id: int,
    ):
        return (
            db.query(Job)
            .filter(Job.email_id == email_id)
            .first()
        )
        # changes made
    @staticmethod
    def find_duplicate(db:Session,job_data:dict):
        company=(job_data.get("company") or "").strip().lower()
        role=(job_data.get("role")or "").strip().lower()
        apply_url=(job_data.get("apply_url")or "").strip().lower()
        jobs=db.query(Job).all()
        for job in jobs:
            old_url=(job.apply_url or "").strip().lower()
            if apply_url and old_url:
                if apply_url==old_url:
                    return job
            elif company and role:
                old_company=(job.company or "").strip().lower()
                old_role=(job.role or "").strip().lower()
                if company==old_company and role ==old_role:
                    return job
        return None


    @staticmethod
    def get_all(db: Session):
        return (  
            db.query(Job)
            .order_by(Job.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        job_id: int,
    ):
        return (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    @staticmethod
    def get_latest(
        db: Session,
        limit: int = 10,
    ):
        return (
            db.query(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_company(
        db: Session,
        company: str,
    ):
        return (
            db.query(Job)
            .filter(Job.company.ilike(f"%{company}%"))
            .all()
        )

    @staticmethod
    def search(
        db: Session,
        company: str | None = None,
        role: str | None = None,
        batch: str | None = None,
    ):
        query = db.query(Job)

        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))

        if role:
            query = query.filter(Job.role.ilike(f"%{role}%"))

        if batch:
            query = query.filter(Job.batch == batch)

        return query.all()

    @staticmethod
    def mark_calendar_synced(
        db: Session,
        job: Job,
        event_id: str,
    ):
        job.calendar_event_id = event_id
        job.calendar_synced = True

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def clear_calendar_sync(
        db: Session,
        job: Job,
    ):
        job.calendar_event_id = None
        job.calendar_synced = False

        db.commit()
        db.refresh(job)

        return job