import os
import re
import json
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from app.prompts.resume_parser_prompt import (
    RESUME_PARSER_SYSTEM_PROMPT,
)

from app.schemas.parsed_resume import ParsedResume
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.prompts.email_classifier import EMAIL_CLASSIFIER_SYSTEM_PROMPT
from app.schemas.email_classification import EmailClassification
from app.schemas.job import Job
from app.prompts.job_parser import JOB_PARSER_SYSTEM_PROMPT
from app.prompts.ats_prompt import (
    ATS_MATCH_PROMPT,
    ats_match_parser,
)

from app.schemas.ats_match import ATSMatchResult
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()


class GroqService:
    """
    Wrapper around Groq LLM.
    """

    MAX_EMAIL_BODY_CHARS = 6000
    MAX_PAGE_TEXT_CHARS = 12000

    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="openai/gpt-oss-120b",
            temperature=0,
        )
        self.job_parser = PydanticOutputParser(
    pydantic_object=Job
)
        self.parser = PydanticOutputParser(
            pydantic_object=EmailClassification
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(
            r"\n{3,}",
            "\n\n",
            (text or "").strip(),
        )

    def _shrink_text(
        self,
        text: str,
        limit: int,
    ) -> str:
        normalized = self._normalize_text(text)

        if len(normalized) <= limit:
            return normalized

        head_len = int(limit * 0.8)
        tail_len = limit - head_len

        head = normalized[:head_len].rstrip()
        tail = normalized[-tail_len:].lstrip()

        return (
            head
            + "\n\n[TRUNCATED FOR MODEL LIMIT]\n\n"
            + tail
        )

    def parse_job(self, page_text: str) -> Job:
        compact_page = self._shrink_text(
            page_text,
            self.MAX_PAGE_TEXT_CHARS,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    JOB_PARSER_SYSTEM_PROMPT + "\n\n{format_instructions}",
                ),
                (
                    "human",
                    "Page text:\n{page}",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "page": compact_page,
                "format_instructions": self.job_parser.get_format_instructions(),
            }
        )

        # First attempt: parse directly
        try:
            job = self.job_parser.parse(response.content)
        except Exception as e:
            # Try to recover JSON from common formats (fenced blocks or raw JSON)
            text = response.content or ""

            # Helper to extract a JSON-like substring
            def _extract_json(candidate: str) -> Optional[str]:
                # fenced ```json ... ``` or ``` ... ```
                m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL)
                if m:
                    return m.group(1)

                # look for first { ... } block
                m2 = re.search(r"(\{.*\})", candidate, flags=re.DOTALL)
                if m2:
                    return m2.group(1)

                # look for first [ ... ] block
                m3 = re.search(r"(\[.*\])", candidate, flags=re.DOTALL)
                if m3:
                    return m3.group(1)

                return None

            extracted = _extract_json(text)

            if extracted:
                try:
                    # sanity-check JSON
                    json.loads(extracted)
                    job = self.job_parser.parse(extracted)
                except Exception:
                    raise OutputParserException(
                        f"Invalid json output (extracted) from Groq:\n{text}"
                    ) from e
            else:
                raise OutputParserException(
                    f"Invalid json output from Groq:\n{text}"
                ) from e

        if not any(
            [
                job.company,
                job.role,
                job.location,
                job.job_description,
                job.apply_url,
                job.ctc,
                job.stipend,
                job.application_deadline,
            ]
        ):
            raise ValueError("Parsed job is empty.")

        return job
    def classify_email(
        self,
        subject: str,
        sender: str,
        body: str,
    ) -> EmailClassification:
        compact_body = self._shrink_text(
            body,
            self.MAX_EMAIL_BODY_CHARS,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    EMAIL_CLASSIFIER_SYSTEM_PROMPT
                    + "\n\n{format_instructions}",
                ),
                (
                    "human",
                    """
Subject:
{subject}

Sender:
{sender}

Email Body:
{body}
""",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "subject": subject,
                "sender": sender,
                "body": compact_body,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        try:
            return self.parser.parse(response.content)

        except Exception as e:
            raise ValueError(
                f"Invalid response from Groq:\n{response.content}"
            ) from e

    def parse_resume(
    self,
    resume_text: str,
) -> ParsedResume:

        parser = PydanticOutputParser(
            pydantic_object=ParsedResume
        )

        prompt = RESUME_PARSER_SYSTEM_PROMPT.format(
            resume=resume_text,
            format_instructions=parser.get_format_instructions(),
        )

        response = self.llm.invoke(prompt)

        parsed_resume = parser.parse(
            response.content
        )

        return parsed_resume

    def match_resume_job(
        self,
        parsed_resume: dict,
        parsed_job: dict,
    ) -> ATSMatchResult:
        """
        Compare a parsed resume against a parsed job description
        and return an ATS analysis.
        """

        prompt = ATS_MATCH_PROMPT.format(
            resume=parsed_resume,
            job=parsed_job,
        )

        response = self.llm.invoke(prompt)

        return ats_match_parser.parse(response.content)
groq_service = GroqService()
