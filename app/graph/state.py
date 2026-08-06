from typing import Optional, TypedDict

from app.schemas.email_classification import EmailClassification


class WorkflowState(TypedDict):
    email_id: int

    email: Optional[dict]

    classification: Optional[EmailClassification]

    recruitsage_url: Optional[str]

    url_valid: bool

    page_html: Optional[str]

    page_text: Optional[str]

    page_title: Optional[str]

    job: Optional[dict]

    job_id: Optional[int]

    status: str

    errors: list[str]

    calendar_event_id: int | None