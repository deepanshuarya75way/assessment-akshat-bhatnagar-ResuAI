from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories.job_repository import JobRepository
from app.schemas.job_response import JobResponse

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=list[JobResponse],
)
def get_jobs(
    db: Session = Depends(get_db),
):
    return JobRepository.get_all(db)


@router.get(
    "/latest",
    response_model=list[JobResponse],
)
def get_latest_jobs(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return JobRepository.get_latest(db, limit)


@router.get(
    "/company/{company}",
    response_model=list[JobResponse],
)
def get_company_jobs(
    company: str,
    db: Session = Depends(get_db),
):
    return JobRepository.get_by_company(db, company)


@router.get(
    "/search",
    response_model=list[JobResponse],
)
def search_jobs(
    company: str | None = None,
    role: str | None = None,
    batch: str | None = None,
    db: Session = Depends(get_db),
):
    return JobRepository.search(
        db,
        company=company,
        role=role,
        batch=batch,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = JobRepository.get_by_id(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job