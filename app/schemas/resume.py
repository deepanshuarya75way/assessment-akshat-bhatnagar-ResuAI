from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResumeResponse(BaseModel):

    id: int

    user_id: int

    file_name: Optional[str]

    file_path: Optional[str]

    resume_text: Optional[str]

    parsed_resume: Optional[dict]

    parser_version: Optional[str]

    last_parsed_at: Optional[datetime]

    ats_score: Optional[int]

    resume_feedback: Optional[dict]

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True