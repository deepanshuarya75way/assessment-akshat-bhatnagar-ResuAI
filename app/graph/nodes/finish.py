import logging

from app.graph.node_utils import update_email_stage
from app.graph.state import WorkflowState


logger = logging.getLogger(__name__)


def finish_node(state: WorkflowState):
    status = state.get("status")

    if not status:
        state["status"] = "FINISHED"
    elif (
        status == "EMAIL_CLASSIFIED"
        and state.get("classification") is not None
        and not state["classification"].is_placement
    ):
        state["status"] = "SKIPPED_NON_PLACEMENT"

    update_email_stage(
        state["email_id"],
        state["status"],
    )
    logger.info(
        "Finishing email %s with status=%s errors=%s",
        state["email_id"],
        state["status"],
        state.get("errors"),
    )

    return state
