from app.graph.state import WorkflowState


def placement_router(state: WorkflowState):

    classification = state.get("classification")

    if classification is None:
        return "finish"

    if classification.is_placement:
        return "extract_link"

    return "finish"


def url_router(state: WorkflowState):

    if state.get("url_valid", False):
        return "playwright_scraper"

    return "finish"


def scrape_router(state: WorkflowState):

    if state.get("status") == "PAGE_SCRAPED":
        return "parse_job"

    return "finish"


def parse_router(state: WorkflowState):

    if state.get("status") == "JOB_PARSED":
        return "save_job"

    return "finish"


def save_router(state: WorkflowState):

    if state.get("status") in {
        "JOB_SAVED",
        "JOB_ALREADY_EXISTS",
    }:
        return "ats_match"

    return "finish"


def ats_router(state: WorkflowState):

    if state.get("status") == "ATS_MATCHED":
        return "calendar_sync"

    return "finish"
