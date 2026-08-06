from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class ATSMatch(Base):

    __tablename__ = "ats_matches"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ----------------------------
    # Relationships
    # ----------------------------

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ----------------------------
    # Scores
    # ----------------------------

    overall_score = Column(
        Integer,
        nullable=False,
    )

    skill_score = Column(
        Integer,
        nullable=False,
    )

    experience_score = Column(
        Integer,
        nullable=False,
    )

    education_score = Column(
        Integer,
        nullable=False,
    )

    keyword_score = Column(
        Integer,
        nullable=False,
    )

    certification_score = Column(
        Integer,
        nullable=False,
    )

    # ----------------------------
    # Match Details
    # ----------------------------

    matched_skills = Column(
        JSONB,
        nullable=True,
    )

    missing_skills = Column(
        JSONB,
        nullable=True,
    )

    suggestions = Column(
        JSONB,
        nullable=True,
    )

    analysis = Column(
        Text,
        nullable=True,
    )

    # ----------------------------
    # Timestamp
    # ----------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ----------------------------
    # Relationships
    # ----------------------------

    resume = relationship(
        "Resume",
        back_populates="ats_matches",
    )

    job = relationship(
        "Job",
        back_populates="ats_matches",
    )
    __table_args__ = (
    UniqueConstraint(
        "resume_id",
        "job_id",
        name="uq_resume_job_match",
    ),
)