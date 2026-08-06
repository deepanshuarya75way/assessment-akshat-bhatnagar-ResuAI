from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False, index=True)

    phone = Column(String)

    college = Column(String)

    branch = Column(String)

    cgpa = Column(Float)

    graduation_year = Column(Integer)

    linkedin_url = Column(String)

    github_url = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    resume = relationship(
        "Resume",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )