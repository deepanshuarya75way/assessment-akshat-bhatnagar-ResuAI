from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.calendar_sync_service import CalendarSyncService

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.post("/sync/{job_id}")
def sync_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return CalendarSyncService.sync_job(
            db=db,
            job_id=job_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.delete("/{job_id}")
def delete_calendar_event(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return CalendarSyncService.delete_job_event(
            db=db,
            job_id=job_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )