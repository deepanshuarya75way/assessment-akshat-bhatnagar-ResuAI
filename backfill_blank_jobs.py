from app.database.session import SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.email_processor import EmailProcessor


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


def main():

    db = SessionLocal()

    try:

        jobs = JobRepository.get_all(db)
        blank_jobs = [job for job in jobs if _is_blank_job(job)]

        print(f"Found {len(blank_jobs)} blank job row(s).")

        for job in blank_jobs:

            print(f"Reprocessing email_id={job.email_id} job_id={job.id}")
            EmailProcessor.process(job.email_id)

        print("Backfill complete.")

    finally:

        db.close()


if __name__ == "__main__":
    main()