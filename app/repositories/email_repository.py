from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.emails import Email


RETRYABLE_STAGES = (
    "EMAIL_SAVED",
    "EMAIL_PROCESSING",
    "EMAIL_CLASSIFIED",
    "INVALID_URL",
    "SCRAPE_FAILED",
    "JOB_PARSE_FAILED",
    "JOB_SAVE_FAILED",
    "FAILED",
)


class EmailRepository:

    @staticmethod
    def update_processing_stage(
        db: Session,
        email_id: int,
        stage: str,
    ):

        email = (
            db.query(Email)
            .filter(Email.id == email_id)
            .first()
        )

        if not email:
            return None

        email.processing_stage = stage

        db.commit()
        db.refresh(email)

        return email

    @staticmethod
    def get_unprocessed(db: Session):

        return (
            db.query(Email)
            .filter(
                Email.processing_stage.in_(RETRYABLE_STAGES)
            )
            .order_by(Email.created_at.asc())
            .all()
        )

    @staticmethod
    def get_processing(db: Session):

        return (
            db.query(Email)
            .filter(Email.processing_stage == "EMAIL_PROCESSING")
            .all()
        )

    @staticmethod
    def get_by_gmail_id(db: Session, gmail_id: str):

        return (
            db.query(Email)
            .filter(Email.gmail_message_id == gmail_id)
            .first()
        )

    @staticmethod
    def create(db: Session, email_data: dict):

        email = Email(**email_data)

        db.add(email)

        try:
            db.commit()
            db.refresh(email)
            return email
        except IntegrityError:
            db.rollback()
            return EmailRepository.get_by_gmail_id(
                db,
                email_data["gmail_message_id"],
            )

    @staticmethod
    def get_all(db: Session):

        return db.query(Email).all()

    @staticmethod
    def mark_processing(db: Session, email_id: int):

        return EmailRepository.update_processing_stage(
            db,
            email_id,
            "EMAIL_PROCESSING",
        )

    
