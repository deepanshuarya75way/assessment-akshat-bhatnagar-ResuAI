from datetime import datetime

from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:

    @staticmethod
    def get_all(db: Session):

        return db.query(Resume).all()

    @staticmethod
    def get_by_id(
        db: Session,
        resume_id: int,
    ):

        return (
            db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: int,
    ):

        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        file_name: str,
        file_path: str,
    ):

        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
        )

        db.add(resume)

        db.commit()

        db.refresh(resume)

        return resume

    @staticmethod
    def delete(
        db: Session,
        resume_id: int,
    ):

        resume = ResumeRepository.get_by_id(
            db,
            resume_id,
        )

        if resume:

            db.delete(resume)

            db.commit()

        return resume

    @staticmethod
    def update_resume_file(
        db: Session,
        user_id: int,
        filename: str,
        filepath: str,
    ):

        resume = ResumeRepository.get_by_user_id(
            db,
            user_id,
        )

        if resume is None:
            return None

        resume.file_name = filename

        resume.file_path = filepath

        # New upload means old parsing is no longer valid
        resume.resume_text = None
        resume.parsed_resume = None
        resume.parser_version = None
        resume.last_parsed_at = None
        resume.ats_score = None
        resume.resume_feedback = None

        db.commit()

        db.refresh(resume)

        return resume

    @staticmethod
    def update_resume_text(
        db: Session,
        user_id: int,
        resume_text: str,
    ):

        resume = ResumeRepository.get_by_user_id(
            db,
            user_id,
        )

        if resume is None:
            return None

        resume.resume_text = resume_text

        db.commit()

        db.refresh(resume)

        return resume

    @staticmethod
    def save_parsed_resume(
        db: Session,
        resume_id: int,
        parsed_resume,
        parser_version: str,
    ):

        resume = ResumeRepository.get_by_id(
            db,
            resume_id,
        )

        if resume is None:
            return None

        resume.parsed_resume = parsed_resume.model_dump()

        resume.parser_version = parser_version

        resume.last_parsed_at = datetime.utcnow()

        db.commit()

        db.refresh(resume)

        return resume

    @staticmethod
    def get_parsed_resume(
        db: Session,
        user_id: int,
    ):

        resume = ResumeRepository.get_by_user_id(
            db,
            user_id,
        )

        if resume is None:
            return None

        return resume.parsed_resume