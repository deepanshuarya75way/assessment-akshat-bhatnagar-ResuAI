from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile
import fitz

UPLOAD_DIR = Path("app/uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ResumeService:

    @staticmethod
    async def save_resume(file: UploadFile):

        extension = Path(file.filename).suffix.lower()

        if extension != ".pdf":
            raise ValueError("Only PDF files are allowed.")

        filename = f"{uuid.uuid4()}{extension}"

        filepath = UPLOAD_DIR / filename

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return filename, str(filepath)
    @staticmethod
    def extract_text(filepath: str):

        doc = fitz.open(filepath)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text.strip()
    