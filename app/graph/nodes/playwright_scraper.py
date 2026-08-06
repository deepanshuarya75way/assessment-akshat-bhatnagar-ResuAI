import logging

from app.graph.node_utils import update_email_stage
from app.graph.state import WorkflowState
from app.services.playwright import playwright_service


logger = logging.getLogger(__name__)


def playwright_scraper_node(state: WorkflowState) -> WorkflowState:
    """
    Scrapes the RecruitSage page using Playwright.
    """

    try:

        url = state["recruitsage_url"]

        if not url:

            state["status"] = "SCRAPE_FAILED"
            state["errors"].append("No RecruitSage URL available.")
            update_email_stage(
                state["email_id"],
                state["status"],
            )

            return state

        logger.info(
            "Scraping RecruitSage page for email %s url=%s",
            state["email_id"],
            url,
        )
        result = playwright_service.scrape(url)

        state["page_html"] = result["html"]

        state["page_text"] = result["text"]

        state["page_title"] = result["title"]

        state["status"] = "PAGE_SCRAPED"
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.info(
            "Scrape complete for email %s title=%r text_len=%s",
            state["email_id"],
            state["page_title"],
            len(state["page_text"] or ""),
        )

        return state

    except Exception as e:

        state["status"] = "SCRAPE_FAILED"

        state["errors"].append(str(e))
        update_email_stage(
            state["email_id"],
            state["status"],
        )
        logger.exception(
            "Scrape failed for email %s",
            state["email_id"],
        )

        return state
