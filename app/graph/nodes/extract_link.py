from app.graph.state import WorkflowState


def extract_link_node(state: WorkflowState):

    classification = state["classification"]

    recruitsage_url = classification.recruitsage_url

    if not recruitsage_url:
        for link in state.get("email", {}).get(
            "links",
            [],
        ):
            if "recruit.thapar.edu" in link:
                recruitsage_url = link.rstrip(".")
                break

    state["recruitsage_url"] = recruitsage_url

    state["status"] = "LINK_EXTRACTED"

    return state
