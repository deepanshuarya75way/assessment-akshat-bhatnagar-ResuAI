from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.ats_matching import ATSMatchingService
from app.schemas.ats_match import ATSMatchResponse
from typing import List
router = APIRouter(
    prefix="/ats",
    tags=["ATS Matching"],
)


@router.post(
    "/match/{user_id}/{job_id}",
    response_model=ATSMatchResponse,
)
def match_resume_with_job(
    user_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ATSMatchingService.match_resume_with_job(
            db=db,
            user_id=user_id,
            job_id=job_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get(
    "/{match_id}",
    response_model=ATSMatchResponse,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ATSMatchingService.get_match(
            db=db,
            match_id=match_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get(
    "/resume/{user_id}",
    response_model=List[ATSMatchResponse],
)
def get_resume_matches(
    user_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ATSMatchingService.get_all_resume_matches(
            db=db,
            user_id=user_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get(
    "/job/{job_id}",
    response_model=List[ATSMatchResponse],
)
def get_job_matches(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ATSMatchingService.get_all_job_matches(
            db=db,
            job_id=job_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{match_id}")
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ATSMatchingService.delete_match(
            db=db,
            match_id=match_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
