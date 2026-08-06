from typing import Optional
from pydantic import BaseModel, Field


class EmailClassification(BaseModel):
    """
    Structured output returned by the LLM after classifying
    a placement email.
    """

    is_placement: bool = Field(
        ...,
        description="True if this email is related to placements, internships, hiring or recruitment."
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )

    company: Optional[str] = Field(
        default=None,
        description="Company name if available."
    )

    role: Optional[str] = Field(
        default=None,
        description="Job role if mentioned."
    )

    recruitsage_url: Optional[str] = Field(
        default=None,
        description="RecruitSage application URL if present."
    )

    deadline: Optional[str] = Field(
        default=None,
        description="Application deadline exactly as mentioned in the email."
    )

    reason: str = Field(
        ...,
        description="Short explanation of why this classification was made."
    )