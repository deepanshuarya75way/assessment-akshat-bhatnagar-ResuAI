from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.sql import func

from app.database.base import Base

class Email(Base):

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    gmail_message_id = Column(
        String,
        unique=True,
        nullable=False
    )

    subject = Column(String)

    sender = Column(String)

    body = Column(Text)

    links = Column(
        JSONB,
        nullable=False,
        default=list
    )

    received_time = Column(DateTime)

    processed = Column(
        Boolean,
        default=False
    )

    processing_stage = Column(
        String,
        default="EMAIL_SAVED"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )