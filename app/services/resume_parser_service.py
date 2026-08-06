import logging
import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.resume_repository import ResumeRepository
from app.services.service_container import ServiceContainer

logger = logging.getLogger(__name__)


class ResumeParserService:

    PARSER_VERSION = "v1"

    @staticmethod
    def parse_resume(
        db: Session,
        user_id: int,
        force: bool = False,
    ):

        logger.info(f"Starting resume parsing for user {user_id}")

        # Fetch Resume
        resume = ResumeRepository.get_by_user_id(
            db,
            user_id,
        )

        if resume is None:
            logger.warning(f"No resume found for user {user_id}")

            raise HTTPException(
                status_code=404,
                detail="Resume not found."
            )

        # Validate extracted text
        if (
            not resume.resume_text
            or len(resume.resume_text.strip()) < 100
        ):

            logger.warning(
                f"Resume text missing or too short for user {user_id}"
            )

            raise HTTPException(
                status_code=400,
                detail="Resume text has not been extracted or is invalid."
            )

        # Skip parsing if already parsed
        if resume.parsed_resume and not force:

            logger.info(
                f"Resume already parsed for user {user_id}"
            )

            return {
                "message": "Resume already parsed.",
                "parser_version": resume.parser_version,
                "resume": resume.parsed_resume,
            }

        start_time = time.time()

        try:

            parsed_resume = ServiceContainer.groq().parse_resume(
                resume.resume_text
            )

        except Exception as e:

            logger.exception(e)

            raise HTTPException(
                status_code=500,
                detail="Failed to parse resume."
            )

        elapsed = round(time.time() - start_time, 2)

        logger.info(
            f"Resume parsed in {elapsed} seconds"
        )

        ResumeRepository.save_parsed_resume(
            db=db,
            resume_id=resume.id,
            parsed_resume=parsed_resume,
            parser_version=self.PARSER_VERSION if False else ResumeParserService.PARSER_VERSION,
        )

        logger.info(
            f"Resume parsing completed for user {user_id}"
        )

        return {
            "message": "Resume parsed successfully.",
            "parser_version": ResumeParserService.PARSER_VERSION,
            "parse_time": elapsed,
            "resume": parsed_resume,
        }