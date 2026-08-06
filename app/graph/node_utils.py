import logging

from app.database.session import SessionLocal
from app.repositories.email_repository import EmailRepository


logger = logging.getLogger(__name__)


def update_email_stage(email_id: int, stage: str) -> None:
    db = SessionLocal()

    try:
        EmailRepository.update_processing_stage(
            db,
            email_id,
            stage,
        )
    except Exception:
        logger.exception(
            "Failed to update email %s stage to %s",
            email_id,
            stage,
        )
    finally:
        db.close()
