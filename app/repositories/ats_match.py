from sqlalchemy.orm import Session

from app.models.ats_match import ATSMatch
from app.schemas.ats_match import ATSMatchResult


class ATSMatchRepository:

    @staticmethod
    def create_match(
        db: Session,
        resume_id: int,
        job_id: int,
        result: ATSMatchResult,
    ) -> ATSMatch:

        ats_match = ATSMatch(
            resume_id=resume_id,
            job_id=job_id,

            overall_score=result.overall_score,
            skill_score=result.skill_score,
            experience_score=result.experience_score,
            education_score=result.education_score,
            keyword_score=result.keyword_score,
            certification_score=result.certification_score,

            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,

            suggestions=result.suggestions,

            analysis=result.analysis,
        )

        db.add(ats_match)
        db.commit()
        db.refresh(ats_match)

        return ats_match

    @staticmethod
    def get_by_id(
        db: Session,
        match_id: int,
    ) -> ATSMatch | None:

        return (
            db.query(ATSMatch)
            .filter(ATSMatch.id == match_id)
            .first()
        )

    @staticmethod
    def upsert_match(
        db: Session,
        resume_id: int,
        job_id: int,
        result: ATSMatchResult,
    ) -> ATSMatch:

        ats_match = (
            db.query(ATSMatch)
            .filter(
                ATSMatch.resume_id == resume_id,
                ATSMatch.job_id == job_id,
            )
            .first()
        )

        if ats_match is None:
            ats_match = ATSMatch(
                resume_id=resume_id,
                job_id=job_id,
            )
            db.add(ats_match)

        ats_match.overall_score = result.overall_score
        ats_match.skill_score = result.skill_score
        ats_match.experience_score = result.experience_score
        ats_match.education_score = result.education_score
        ats_match.keyword_score = result.keyword_score
        ats_match.certification_score = result.certification_score

        ats_match.matched_skills = result.matched_skills
        ats_match.missing_skills = result.missing_skills
        ats_match.suggestions = result.suggestions
        ats_match.analysis = result.analysis

        db.commit()
        db.refresh(ats_match)

        return ats_match

    @staticmethod
    def get_all_for_resume(
        db: Session,
        resume_id: int,
    ) -> list[ATSMatch]:

        return (
            db.query(ATSMatch)
            .filter(ATSMatch.resume_id == resume_id)
            .all()
        )

    @staticmethod
    def get_all_for_job(
        db: Session,
        job_id: int,
    ) -> list[ATSMatch]:

        return (
            db.query(ATSMatch)
            .filter(ATSMatch.job_id == job_id)
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        match_id: int,
    ) -> bool:

        ats_match = (
            db.query(ATSMatch)
            .filter(ATSMatch.id == match_id)
            .first()
        )

        if not ats_match:
            return False

        db.delete(ats_match)
        db.commit()

        return True