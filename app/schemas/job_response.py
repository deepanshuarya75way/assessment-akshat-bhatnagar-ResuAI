from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):

    id: int

    company: str | None

    role: str | None

    job_type: str | None

    location: str | None

    ctc: str | None

    stipend: str | None

    eligible_branches: list[str]

    minimum_cgpa: str | None

    batch: str | None

    application_deadline: str | None

    selection_process: list[str]

    job_description: str | None

    skills_required: list[str]

    apply_url: str | None

    calendar_event_id: str | None = None
    calendar_synced: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)