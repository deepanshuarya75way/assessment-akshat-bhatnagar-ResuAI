from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.repositories.resume_repository import ResumeRepository

from app.services.resume_service import ResumeService
from app.services.resume_parser_service import ResumeParserService
from app.services.ats_matching import ATSMatchingService
from app.schemas.resume import ResumeResponse

router = APIRouter(
    prefix="/resumes",
    tags=["Resume"],
)


# ---------------------------------------------------
# Get All Resumes
# ---------------------------------------------------

@router.get("/", response_model=list[ResumeResponse])
def get_all_resumes(
    db: Session = Depends(get_db),
):

    return ResumeRepository.get_all(db)


# ---------------------------------------------------
# Get Resume By ID
# ---------------------------------------------------

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):

    resume = ResumeRepository.get_by_id(
        db,
        resume_id,
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return resume


# ---------------------------------------------------
# Delete Resume
# ---------------------------------------------------

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):

    resume = ResumeRepository.delete(
        db,
        resume_id,
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return {
        "message": "Resume deleted successfully."
    }


# ---------------------------------------------------
# Upload Resume
# ---------------------------------------------------

@router.post("/upload/{user_id}")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    try:

        filename, filepath = await ResumeService.save_resume(file)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    resume = ResumeRepository.get_by_user_id(
        db,
        user_id,
    )

    if resume:

        resume = ResumeRepository.update_resume_file(
            db,
            user_id,
            filename,
            filepath,
        )

    else:

        resume = ResumeRepository.create(
            db,
            user_id,
            filename,
            filepath,
        )

    # ---------------------------------------
# Extract Resume Text
# ---------------------------------------

    text = ResumeService.extract_text(
        resume.file_path,
    )

    ResumeRepository.update_resume_text(
        db,
        user_id,
        text,
    )

    # ---------------------------------------
    # Parse Resume
    # ---------------------------------------

    ResumeParserService.parse_resume(
        db=db,
        user_id=user_id,
        force=True,
    )

    # ---------------------------------------
    # Recompute ATS
    # ---------------------------------------

    ATSMatchingService.recompute_for_user(
        db=db,
        user_id=user_id,
    )

    return {
        "message": "Resume uploaded, parsed and ATS updated successfully.",
        "resume": resume,
    }


# ---------------------------------------------------
# Extract Resume Text
# ---------------------------------------------------

@router.post("/extract/{user_id}")
def extract_resume_text(
    user_id: int,
    db: Session = Depends(get_db),
):

    resume = ResumeRepository.get_by_user_id(
        db,
        user_id,
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    if not resume.file_path:
        raise HTTPException(
            status_code=400,
            detail="Resume PDF not uploaded.",
        )

    text = ResumeService.extract_text(
        resume.file_path,
    )

    ResumeRepository.update_resume_text(
        db,
        user_id,
        text,
    )

    return {
        "message": "Resume text extracted successfully.",
        "characters": len(text),
    }


# ---------------------------------------------------
# Parse Resume
# ---------------------------------------------------

@router.post("/parse/{user_id}")
def parse_resume(
    user_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):

    return ResumeParserService.parse_resume(
        db=db,
        user_id=user_id,
        force=force,
    )


# ---------------------------------------------------
# Get Parsed Resume
# ---------------------------------------------------

@router.get("/parsed/{user_id}")
def get_parsed_resume(
    user_id: int,
    db: Session = Depends(get_db),
):

    parsed_resume = ResumeRepository.get_parsed_resume(
        db,
        user_id,
    )

    if parsed_resume is None:
        raise HTTPException(
            status_code=404,
            detail="Parsed resume not found.",
        )

    return parsed_resume