from typing import Optional

from pydantic import BaseModel, Field


class Education(BaseModel):

    degree: str = Field(
        description="Degree earned by the candidate"
    )

    institution: str = Field(
        description="College or University name"
    )

    cgpa: Optional[str] = Field(
        default=None,
        description="CGPA or percentage"
    )

    start_year: Optional[str] = None

    end_year: Optional[str] = None


class Experience(BaseModel):

    company: str

    role: str

    duration: Optional[str] = None

    description: Optional[str] = None


class Project(BaseModel):

    title: str

    description: Optional[str] = None

    technologies: list[str] = []


class ParsedResume(BaseModel):

    name: str

    email: str

    phone: str

    linkedin: Optional[str] = None

    github: Optional[str] = None

    portfolio: Optional[str] = None

    location: Optional[str] = None

    summary: Optional[str] = None

    skills: list[str] = []

    education: list[Education] = []

    experience: list[Experience] = []

    projects: list[Project] = []

    certifications: list[str] = []

    achievements: list[str] = []

    languages: list[str] = []