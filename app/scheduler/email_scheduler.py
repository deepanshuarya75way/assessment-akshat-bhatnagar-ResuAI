import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING

from app.database.session import SessionLocal
from app.repositories.email_repository import EmailRepository
from app.services.email_processor import EmailProcessor
from app.services.gmail import GmailService

scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Kolkata"))
logger = logging.getLogger(__name__)


def _log_next_run_time() -> None:
    job = scheduler.get_job("gmail_scheduler")

    if job is None:
        logger.warning("Scheduler job gmail_scheduler was not found")
        return

    logger.info(
        "Next scheduled Gmail sync at %s",
        job.next_run_time.strftime("%d-%m-%Y %H:%M:%S"),
    )


def sync_and_process_emails():

    print("\n" + "=" * 70)
    print(f"Scheduler Run : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    print("=" * 70)

    gmail_service = GmailService()
    logger.info("Starting Gmail sync run")
    emails = []

    try:
        emails = gmail_service.read_latest_emails()
    except Exception as e:
        print(f"Gmail Error : {e}")
        logger.exception("Gmail sync failed")
        logger.warning(
            "Continuing with pending emails already stored in the database"
        )

    db = SessionLocal()

    try:

        new_emails = 0

        for email in emails:

            existing = EmailRepository.get_by_gmail_id(
                db,
                email["gmail_message_id"],
            )

            if existing:
                continue

            EmailRepository.create(
                db,
                email,
            )

            new_emails += 1

        print(f"New Emails Saved : {new_emails}")
        logger.info("Saved %s new emails", new_emails)

        pending = EmailRepository.get_unprocessed(db)

        print(f"Pending Emails : {len(pending)}")
        logger.info(
            "Found %s pending/retryable emails",
            len(pending),
        )

        workflow_completed = 0
        jobs_persisted = 0
        failed = 0

        for email in pending:

            try:

                print(f"Processing Email ID : {email.id}")
                logger.info(
                    "Processing email_id=%s stage=%s subject=%r",
                    email.id,
                    email.processing_stage,
                    email.subject,
                )

                result = EmailProcessor.process(email.id)

                if result.get("job_id") is not None:
                    jobs_persisted += 1

                if result.get("errors"):
                    failed += 1
                    logger.error(
                        "Email %s finished with status=%s errors=%s",
                        email.id,
                        result.get("status"),
                        result.get("errors"),
                    )
                else:
                    workflow_completed += 1
                    logger.info(
                        "Email %s completed with status=%s job_id=%s",
                        email.id,
                        result.get("status"),
                        result.get("job_id"),
                    )

            except Exception as e:

                failed += 1

                print(
                    f"Failed Processing Email {email.id} : {e}"
                )
                logger.exception(
                    "Unhandled scheduler failure for email %s",
                    email.id,
                )

        print("-" * 70)
        print(
            f"Workflow Completed     : {workflow_completed}"
        )
        print(f"Jobs Persisted         : {jobs_persisted}")
        print(f"Failed                : {failed}")
        print("=" * 70)
        logger.info(
            "Run summary workflow_completed=%s jobs_persisted=%s failed=%s",
            workflow_completed,
            jobs_persisted,
            failed,
        )

    except Exception as e:

        print(f"Scheduler Error : {e}")
        logger.exception("Scheduler run failed")

    finally:

        db.close()


def start_scheduler():

    scheduler.add_job(
        sync_and_process_emails,
        trigger="interval",
        minutes=5,          # Change to 5 or 10 in production
        id="gmail_scheduler",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    if scheduler.state != STATE_RUNNING:

        scheduler.start()

        print("Scheduler Started")
        _log_next_run_time()

    else:

        print("Scheduler Already Running")
        _log_next_run_time()
