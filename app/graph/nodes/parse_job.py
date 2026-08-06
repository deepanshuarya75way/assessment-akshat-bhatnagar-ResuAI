import logging

from app.graph.node_utils import update_email_stage
from app.graph.state import WorkflowState
from app.services.service_container import ServiceContainer


logger = logging.getLogger(__name__)


def parse_job_node(state: WorkflowState) -> WorkflowState:
    """
    Uses Groq to extract structured job data
    from the scraped placement page.
    """

    try:

        page_text = state.get("page_text")

        if not page_text:

            state["status"] = "JOB_PARSE_FAILED"

            state["errors"].append(
                "Page text not found."
            )
            update_email_stage(
                state["email_id"],
                state["status"],
            )

            return state

        logger.info(
            "Parsing job for email %s page_text_len=%s",
            state["email_id"],
            len(page_text),
        )
        job = ServiceContainer.groq().parse_job(page_text)

        state["job"] = job.model_dump()

        state["status"] = "JOB_PARSED"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "Parsed job for email %s company=%r role=%r",
            state["email_id"],
            state["job"].get("company"),
            state["job"].get("role"),
        )

        return state

    except Exception as e:

        state["status"] = "JOB_PARSE_FAILED"

        state["errors"].append(str(e))
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.exception(
            "Job parsing failed for email %s",
            state["email_id"],
        )

        return state
