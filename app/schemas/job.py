from typing import Optional

from pydantic import BaseModel, Field


class Job(BaseModel):
    company: Optional[str] = None

    role: Optional[str] = None

    job_type: Optional[str] = None

    location: Optional[str] = None

    ctc: Optional[str] = None

    stipend: Optional[str] = None

    eligible_branches: list[str] = Field(default_factory=list)

    minimum_cgpa: Optional[str] = None

    batch: Optional[str] = None

    application_deadline: Optional[str] = None

    selection_process: list[str] = Field(default_factory=list)

    job_description: Optional[str] = None

    skills_required: list[str] = Field(default_factory=list)

    apply_url: Optional[str] = None