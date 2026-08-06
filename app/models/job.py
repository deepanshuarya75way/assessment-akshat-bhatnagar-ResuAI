from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email_id = Column(
        Integer,
        ForeignKey(
            "emails.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    company = Column(String)

    role = Column(String)

    job_type = Column(String)

    location = Column(String)

    ctc = Column(String)

    stipend = Column(String)

    minimum_cgpa = Column(String)

    batch = Column(String)

    application_deadline = Column(String)

    eligible_branches = Column(
        JSONB,
        default=list,
    )

    selection_process = Column(
        JSONB,
        default=list,
    )

    skills_required = Column(
        JSONB,
        default=list,
    )

    job_description = Column(Text)

    apply_url = Column(String)
    calendar_event_id = Column(
        String,
        nullable=True,
    )

    calendar_synced = Column(
        Boolean,
        default=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    email = relationship("Email")

    ats_matches = relationship(
        "ATSMatch",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    # ---------------------------------------------------
    # Helper method for ATS / LLM
    # ---------------------------------------------------

    def to_parsed_job(self) -> dict:

        return {
            "company": self.company,
            "role": self.role,
            "job_type": self.job_type,
            "location": self.location,
            "ctc": self.ctc,
            "stipend": self.stipend,
            "minimum_cgpa": self.minimum_cgpa,
            "batch": self.batch,
            "application_deadline": self.application_deadline,
            "eligible_branches": self.eligible_branches or [],
            "selection_process": self.selection_process or [],
            "skills_required": self.skills_required or [],
            "job_description": self.job_description or "",
            "apply_url": self.apply_url or "",
        }