import logging

from app.graph.state import WorkflowState
from app.graph.node_utils import update_email_stage
from app.database.session import SessionLocal

from app.repositories.user_repository import UserRepository

from app.services.ats_matching import ATSMatchingService


logger = logging.getLogger(__name__)


def ats_match_node(state: WorkflowState):

    db = SessionLocal()

    try:

        if state.get("job_id") is None:
            state["status"] = "ATS_MATCH_FAILED"
            state["errors"].append("Job ID not found.")
            update_email_stage(
                state["email_id"],
                state["status"],
            )
            return state

        users = UserRepository.get_all(db)
        matched_users = 0

        for user in users:

            if (
                user.resume
                and user.resume.parsed_resume
            ):

                try:

                    ATSMatchingService.match_resume_with_job(
                        db=db,
                        user_id=user.id,
                        job_id=state["job_id"],
                    )
                    matched_users += 1

                except Exception:
                    logger.exception(
                        "ATS match failed for user %s job %s",
                        user.id,
                        state["job_id"],
                    )
                    continue

        state["status"] = "ATS_MATCHED"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "ATS matching complete for email %s job_id=%s matched_users=%s",
            state["email_id"],
            state["job_id"],
            matched_users,
        )

        return state

    except Exception as e:
        state["status"] = "ATS_MATCH_FAILED"
        state["errors"].append(str(e))
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.exception(
            "ATS matching failed for email %s",
            state["email_id"],
        )
        return state

    finally:

        db.close()
