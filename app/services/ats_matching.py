from sqlalchemy.orm import Session

from app.repositories.resume_repository import ResumeRepository
from app.repositories.job_repository import JobRepository
from app.repositories.ats_match import ATSMatchRepository

from app.services.service_container import ServiceContainer

from app.repositories.job_repository import JobRepository

class ATSMatchingService:

    @staticmethod
    def match_resume_with_job(
        db: Session,
        user_id: int,
        job_id: int,
    ):

        # -------------------------
        # Fetch Resume
        # -------------------------

        resume = ResumeRepository.get_by_user_id(
            db=db,
            user_id=user_id,
        )

        if resume is None:
            raise ValueError("Resume not found.")

        if resume.parsed_resume is None:
            raise ValueError("Resume has not been parsed.")

        # -------------------------
        # Fetch Job
        # -------------------------

        job = JobRepository.get_by_id(
            db=db,
            job_id=job_id,
        )

        if job is None:
            raise ValueError("Job not found.")

        if not job.skills_required and not job.job_description:
            raise ValueError("Job information is incomplete.")

        # -------------------------
        # Build Parsed Job
        # -------------------------

        parsed_job = {
            "company": job.company,
            "role": job.role,
            "job_type": job.job_type,
            "location": job.location,
            "ctc": job.ctc,
            "stipend": job.stipend,
            "minimum_cgpa": job.minimum_cgpa,
            "batch": job.batch,
            "application_deadline": job.application_deadline,
            "eligible_branches": job.eligible_branches,
            "selection_process": job.selection_process,
            "skills_required": job.skills_required,
            "job_description": job.job_description,
            "apply_url": job.apply_url,
        }

        # -------------------------
        # ATS Matching
        # -------------------------

        ats_result = ServiceContainer.groq().match_resume_job(
            parsed_resume=resume.parsed_resume,
            parsed_job=parsed_job,
        )

        # -------------------------
        # Save Result
        # -------------------------

        ats_match = ATSMatchRepository.upsert_match(
            db=db,
            resume_id=resume.id,
            job_id=job.id,
            result=ats_result,
        )

        return ats_match

    @staticmethod
    def get_match(
        db: Session,
        match_id: int,
    ):

        ats_match = ATSMatchRepository.get_by_id(
            db=db,
            match_id=match_id,
        )

        if ats_match is None:
            raise ValueError("ATS Match not found.")

        return ats_match

    @staticmethod
    def get_all_resume_matches(
        db: Session,
        user_id: int,
    ):

        resume = ResumeRepository.get_by_user_id(
            db=db,
            user_id=user_id,
        )

        if resume is None:
            raise ValueError("Resume not found.")

        return ATSMatchRepository.get_all_for_resume(
            db=db,
            resume_id=resume.id,
        )

    @staticmethod
    def get_all_job_matches(
        db: Session,
        job_id: int,
    ):

        job = JobRepository.get_by_id(
            db=db,
            job_id=job_id,
        )

        if job is None:
            raise ValueError("Job not found.")

        return ATSMatchRepository.get_all_for_job(
            db=db,
            job_id=job.id,
        )

    @staticmethod
    def delete_match(
        db: Session,
        match_id: int,
    ):

        deleted = ATSMatchRepository.delete(
            db=db,
            match_id=match_id,
        )

        if not deleted:
            raise ValueError("ATS Match not found.")

        return {
            "message": "ATS Match deleted successfully."
        }


    @staticmethod
    def recompute_for_user(
        db: Session,
        user_id: int,
    ):

        jobs = JobRepository.get_all(db)

        for job in jobs:

            try:

                ATSMatchingService.match_resume_with_job(
                    db=db,
                    user_id=user_id,
                    job_id=job.id,
                )

            except Exception:
                # Ignore jobs that cannot be matched
                # (missing data, invalid job, etc.)
                continue