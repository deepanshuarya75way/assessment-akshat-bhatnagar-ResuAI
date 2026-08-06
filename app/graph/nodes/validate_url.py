import logging
from urllib.parse import urlparse

from app.graph.node_utils import update_email_stage
from app.graph.state import WorkflowState


SUPPORTED_DOMAINS = {
    "recruit.thapar.edu",
}

logger = logging.getLogger(__name__)


def validate_url_node(state: WorkflowState) -> WorkflowState:
    """
    Validates whether the extracted RecruitSage URL
    can be scraped safely.
    """

    state["url_valid"] = False

    url = state.get("recruitsage_url")

    if not url:

        state["status"] = "SKIPPED_NO_RECRUITSAGE_URL"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "Email %s has no RecruitSage URL and was skipped",
            state["email_id"],
        )

        return state

    try:

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):

            state["status"] = "INVALID_URL"

            state["errors"].append(
                "Invalid URL scheme."
            )
            update_email_stage(
                state["email_id"],
                state["status"],
            )

            return state

        domain = parsed.netloc.lower()

        if not any(
            domain.endswith(d)
            for d in SUPPORTED_DOMAINS
        ):

            state["status"] = "INVALID_URL"

            state["errors"].append(
                f"Unsupported domain: {domain}"
            )
            update_email_stage(
                state["email_id"],
                state["status"],
            )
            logger.warning(
                "Email %s has unsupported domain %s",
                state["email_id"],
                domain,
            )

            return state

        state["url_valid"] = True

        state["status"] = "URL_VALID"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "Email %s URL validated for domain %s",
            state["email_id"],
            domain,
        )

        return state

    except Exception as e:

        state["status"] = "INVALID_URL"

        state["errors"].append(str(e))
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.exception(
            "URL validation failed for email %s",
            state["email_id"],
        )

        return state
