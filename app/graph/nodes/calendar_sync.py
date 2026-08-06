import logging

from app.graph.state import WorkflowState
from app.graph.node_utils import update_email_stage
from app.database.session import SessionLocal

from app.services.calendar_sync_service import CalendarSyncService


logger = logging.getLogger(__name__)


def calendar_sync_node(state: WorkflowState):

    db = SessionLocal()

    try:

        if state.get("job_id") is None:

            state["status"] = "CALENDAR_SYNC_FAILED"

            state["errors"].append(
                "Job ID not found."
            )
            update_email_stage(
                state["email_id"],
                state["status"],
            )

            return state

        logger.info(
            "Syncing calendar for email %s job_id=%s",
            state["email_id"],
            state["job_id"],
        )
        result = CalendarSyncService.sync_job(
            db=db,
            job_id=state["job_id"],
        )

        state["calendar_event_id"] = result["event_id"]

        state["status"] = "CALENDAR_SYNCED"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "Calendar synced for email %s event_id=%s",
            state["email_id"],
            state["calendar_event_id"],
        )

        return state

    except Exception as e:

        state["status"] = "CALENDAR_SYNC_FAILED"

        state["errors"].append(str(e))
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.exception(
            "Calendar sync failed for email %s",
            state["email_id"],
        )

        return state

    finally:

        db.close()
