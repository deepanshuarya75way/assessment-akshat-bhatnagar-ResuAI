import logging

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.graph.state import WorkflowState
from app.graph.node_utils import update_email_stage
from app.models.emails import Email
from app.services.service_container import ServiceContainer


logger = logging.getLogger(__name__)


def classify_email_node(state: WorkflowState) -> WorkflowState:
    """
    Classifies whether an email is placement related.

    Updates:
        state["classification"]
        state["recruitsage_url"]
        state["status"]
    """

    db: Session = SessionLocal()

    try:

        email = db.query(Email).filter(
            Email.id == state["email_id"]
        ).first()

        if email is None:

            state["status"] = "FAILED"
            state["errors"].append("Email not found.")
            logger.warning(
                "Email %s not found during classification",
                state["email_id"],
            )

            return state

        logger.info(
            "Classifying email_id=%s subject=%r",
            state["email_id"],
            email.subject,
        )

        result = ServiceContainer.groq().classify_email(
            subject=email.subject or "",
            sender=email.sender or "",
            body=email.body or "",
        )

        state["classification"] = result

        state["recruitsage_url"] = result.recruitsage_url

        state["status"] = "EMAIL_CLASSIFIED"

        email.processing_stage = "EMAIL_CLASSIFIED"

        db.commit()
        logger.info(
            "Email %s classified as placement=%s recruitsage_url=%r",
            state["email_id"],
            result.is_placement,
            result.recruitsage_url,
        )

        return state

    except Exception as e:

        db.rollback()

        state["status"] = "FAILED"

        state["errors"].append(str(e))
        logger.exception(
            "Classification failed for email %s",
            state["email_id"],
        )

        email = db.query(Email).filter(
            Email.id == state["email_id"]
        ).first()

        if email:

            email.processing_stage = "FAILED"
            db.commit()

        return state

    finally:

        db.close()
