from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    file_name = Column(
        String,
        nullable=False,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    resume_text = Column(
        Text,
        nullable=True,
    )

    # ----------------------------
    # Parsed Resume
    # ----------------------------

    parsed_resume = Column(
        JSONB,
        nullable=True,
    )

    parser_version = Column(
        String,
        nullable=True,
    )

    last_parsed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ----------------------------
    # ATS (Future)
    # ----------------------------

    ats_score = Column(
        Integer,
        nullable=True,
    )

    resume_feedback = Column(
        JSONB,
        nullable=True,
    )

    # ----------------------------
    # Timestamps
    # ----------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ----------------------------
    # Relationship
    # ----------------------------

    user = relationship(
        "User",
        back_populates="resume",
    )
    ats_matches = relationship(
    "ATSMatch",
    back_populates="resume",
    cascade="all, delete-orphan",
)