from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.schemas.ats_match import ATSMatchResult

ats_match_parser = PydanticOutputParser(
    pydantic_object=ATSMatchResult
)

ATS_MATCH_PROMPT = PromptTemplate(
    template="""
You are an expert Applicant Tracking System (ATS) and technical recruiter.

Your task is to compare the candidate's parsed resume with the parsed job description.

Resume:
{resume}

Job Description:
{job}

Evaluate the resume on the following criteria:

1. Skill Match (0-100)
2. Experience Match (0-100)
3. Education Match (0-100)
4. Keyword Match (0-100)
5. Certification Match (0-100)

Then compute an overall ATS score (0-100).

Return:

- overall_score
- skill_score
- experience_score
- education_score
- keyword_score
- certification_score

Also identify:

- matched_skills
- missing_skills
- strengths
- weaknesses
- suggestions

Analysis should briefly explain:
- why the score was given
- major strengths
- major missing requirements

Important Rules:

- Only use information present in the resume and job description.
- Never hallucinate skills or experience.
- If a field is missing, assume it is absent.
- Suggestions should be actionable.
- Missing skills should only include skills explicitly required in the job.
- Output ONLY valid JSON.

{format_instructions}
""",
    input_variables=[
        "resume",
        "job",
    ],
    partial_variables={
        "format_instructions": ats_match_parser.get_format_instructions()
    },
)