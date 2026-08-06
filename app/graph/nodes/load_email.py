from app.database.session import SessionLocal
from app.models.emails import Email


def load_email_node(state):

    db = SessionLocal()

    try:

        email = (
            db.query(Email)
            .filter(Email.id == state["email_id"])
            .first()
        )

        if email is None:

            state["errors"].append("Email not found")

            return state

        state["email"] = {

            "id": email.id,

            "gmail_message_id": email.gmail_message_id,

            "subject": email.subject,

            "sender": email.sender,

            "body": email.body,

            "links": email.links,

            "processed": email.processed,

            "received_time": email.received_time

        }

        return state

    finally:

        db.close()