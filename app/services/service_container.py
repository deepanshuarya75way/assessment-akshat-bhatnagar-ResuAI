from app.services.gmail import GmailService
from app.services.groq import GroqService


class ServiceContainer:

    gmail_service: GmailService | None = None
    groq_service: GroqService | None = None

    @classmethod
    def initialize(cls):

        if cls.gmail_service is None:
            cls.gmail_service = GmailService()

        if cls.groq_service is None:
            cls.groq_service = GroqService()

    @classmethod
    def gmail(cls) -> GmailService:

        if cls.gmail_service is None:
            raise RuntimeError(
                "ServiceContainer has not been initialized."
            )

        return cls.gmail_service

    @classmethod
    def groq(cls) -> GroqService:

        if cls.groq_service is None:
            raise RuntimeError(
                "ServiceContainer has not been initialized."
            )

        return cls.groq_service