from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):

    name: str

    email: str

    phone: str | None = None

    college: str | None = None

    branch: str | None = None

    cgpa: float | None = None

    graduation_year: int | None = None

    linkedin_url: str | None = None

    github_url: str | None = None


class UserUpdate(BaseModel):

    name: str | None = None

    phone: str | None = None

    college: str | None = None

    branch: str | None = None

    cgpa: float | None = None

    graduation_year: int | None = None

    linkedin_url: str | None = None

    github_url: str | None = None


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    name: str

    email: str

    phone: str | None

    college: str | None

    branch: str | None

    cgpa: float | None

    graduation_year: int | None

    linkedin_url: str | None

    github_url: str | None