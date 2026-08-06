from langgraph.graph import StateGraph, START, END
from app.graph.nodes.ats_match import ats_match_node
from app.graph.state import WorkflowState
from app.graph.nodes.parse_job import parse_job_node
from app.graph.router import ats_router
from app.graph.router import parse_router
from app.graph.router import placement_router
from app.graph.router import save_router
from app.graph.router import scrape_router
from app.graph.router import url_router
from app.graph.nodes.load_email import load_email_node
from app.graph.nodes.classify_email import classify_email_node
from app.graph.nodes.extract_link import extract_link_node
from app.graph.nodes.validate_url import validate_url_node
from app.graph.nodes.playwright_scraper import playwright_scraper_node
from app.graph.nodes.finish import finish_node
from app.graph.nodes.calendar_sync import calendar_sync_node
from app.graph.nodes.save_job import save_job_node

builder = StateGraph(WorkflowState)

# -------------------
# Register Nodes
# -------------------

builder.add_node("load_email", load_email_node)

builder.add_node("classify_email", classify_email_node)

builder.add_node("extract_link", extract_link_node)

builder.add_node("validate_url", validate_url_node)

builder.add_node("playwright_scraper", playwright_scraper_node)

builder.add_node("finish", finish_node)
builder.add_node(
    "parse_job",
    parse_job_node,
)
builder.add_node(
    "save_job",
    save_job_node,
)
builder.add_node(
    "calendar_sync",
    calendar_sync_node,
)
builder.add_node(
    "ats_match",
    ats_match_node,
)
# -------------------
# Edges
# -------------------

builder.add_edge(START, "load_email")

builder.add_edge("load_email", "classify_email")

builder.add_conditional_edges(
    "classify_email",
    placement_router,
)

builder.add_edge(
    "extract_link",
    "validate_url",
)

builder.add_conditional_edges(
    "validate_url",
    url_router,
)

builder.add_conditional_edges(
    "playwright_scraper",
    scrape_router,
)

builder.add_conditional_edges(
    "parse_job",
    parse_router,
)

builder.add_conditional_edges(
    "save_job",
    save_router,
)

builder.add_conditional_edges(
    "ats_match",
    ats_router,
)

builder.add_edge(
    "calendar_sync",
    "finish",
)
builder.add_edge(
    "finish",
    END,
)

placement_graph = builder.compile()
