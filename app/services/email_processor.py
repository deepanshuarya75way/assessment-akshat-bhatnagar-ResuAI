# from app.graph.builder import placement_graph


# class EmailProcessor:

#     @staticmethod
#     def process(email_id: int):

#         initial_state = {
#             "email_id": email_id,
#             "email": None,
#             "classification": None,
#             "recruitsage_url": None,
#             "url_valid": False,
#             "page_html": None,
#             "page_text": None,
#             "page_title": None,
#             "job": None,
#             "job_id": None,
#             "status": "GRAPH_STARTED",
#             "errors": [],
#         }

#         return placement_graph.invoke(initial_state)


import logging

from app.database.session import SessionLocal
from app.graph.builder import placement_graph
from app.repositories.email_repository import EmailRepository


logger = logging.getLogger(__name__)


class EmailProcessor:

    @staticmethod
    def process(email_id: int):

        db = SessionLocal()

        try:

            EmailRepository.mark_processing(db, email_id)

        finally:

            db.close()

        initial_state = {

            "email_id": email_id,

            "email": None,

            "classification": None,

            "recruitsage_url": None,

            "url_valid": False,

            "page_html": None,

            "page_text": None,

            "page_title": None,

            "job": None,

            "job_id": None,

            "status": "GRAPH_STARTED",

            "errors": [],
        }

        logger.info("Starting graph for email_id=%s", email_id)
        result = placement_graph.invoke(initial_state)
        logger.info(
            "Finished graph for email_id=%s status=%s job_id=%s errors=%s",
            email_id,
            result.get("status"),
            result.get("job_id"),
            result.get("errors"),
        )
        return result
