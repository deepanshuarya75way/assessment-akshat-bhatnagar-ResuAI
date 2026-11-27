import logging

from app.graph.state import WorkflowState
from app.database.session import SessionLocal
from app.repositories.job_repository import JobRepository
from app.repositories.email_repository import EmailRepository


logger = logging.getLogger(__name__)


def _is_blank_job(job) -> bool:

    return not any(
        [
            job.company,
            job.role,
            job.job_type,
            job.location,
            job.ctc,
            job.stipend,
            job.minimum_cgpa,
            job.batch,
            job.application_deadline,
            job.job_description,
            job.apply_url,
            job.eligible_branches,
            job.selection_process,
            job.skills_required,
        ]
    )


def save_job_node(state: WorkflowState):

    db = SessionLocal()

    try:

        if state.get("job") is None:

            state["status"] = "JOB_SAVE_FAILED"

            state["errors"].append(
                "No parsed job found."
            )
            EmailRepository.update_processing_stage(
                db,
                state["email_id"],
                state["status"],
            )

            return state
        job_data=state["job"]
        existing = JobRepository.get_by_email(
            db,
            state["email_id"],
        )

        if existing:

            if _is_blank_job(existing):

                updated_job = JobRepository.update(
                    db,
                    existing,
                    state["job"],
                )

                state["job_id"] = updated_job.id

                EmailRepository.update_processing_stage(
                    db,
                    state["email_id"],
                    "JOB_SAVED",
                )

                state["status"] = "JOB_SAVED"
                logger.info(
                    "Updated blank job for email %s job_id=%s",
                    state["email_id"],
                    updated_job.id,
                )

                return state

            state["job_id"] = existing.id

            state["status"] = "JOB_ALREADY_EXISTS"

            EmailRepository.update_processing_stage(
                db,
                state["email_id"],
                "JOB_ALREADY_EXISTS",
            )
            logger.info(
                "Job already exists for email %s job_id=%s",
                state["email_id"],
                existing.id,
            )

            return state
        duplicate=JobRepository.find_duplicate(db,job_data)
        if duplicate:
            state["job_id"]=duplicate.id
            state["status"]="Job_already_exists"


            EmailRepository.update_processing_stage(
            db,
            state["email_id"],
            state["status"],
            )
            logger.info("Duplicate job found. Reusing job ID %s",duplicate.id,)
        
            return state
    
        saved_job=JobRepository.create(db,job_data=job_data,email_id=state["email_id"],)
        state["job_id"]=saved_job.id
        state["status"]="JOB_SAVED"
        EmailRepository.update_processing_stage(
            db,state["email_id"],state["status"],
        )
        logger.info("Job saved successfully with ID %s",saved_job.id)
        return state
    except Exception as e:

        db.rollback()

        state["status"] = "JOB_SAVE_FAILED"

        state["errors"].append(str(e))
        logger.exception(
            "Job save failed for email %s",
            state["email_id"],
        )
        EmailRepository.update_processing_stage(
            db,
            state["email_id"],
            state["status"],
        )

        return state

    finally:

        db.close()
