# RESUAI — AI-Powered Placement Copilot

RESUAI is an AI-powered backend application that automates the complete campus placement workflow. It continuously monitors Gmail for placement emails, classifies them using an LLM, scrapes RecruitSage job pages, parses job details, performs ATS matching against uploaded resumes, and synchronizes application deadlines to Google Calendar.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Create & Activate a Virtual Environment](#3-create--activate-a-virtual-environment)
4. [Install Dependencies](#4-install-dependencies)
5. [PostgreSQL Setup](#5-postgresql-setup)
6. [Google Cloud Setup](#6-google-cloud-setup)
7. [Gmail Authentication](#7-gmail-authentication)
8. [RecruitSage Login](#8-recruitsage-login)
9. [Database Initialization](#9-database-initialization)
10. [Run the Application](#10-run-the-application)
11. [End-to-End Workflow](#11-end-to-end-workflow)
12. [Common Issues](#12-common-issues)
13. [Folder Structure](#13-folder-structure)
14. [Tech Stack](#14-tech-stack)
15. [Author](#author)

---

## 1. Prerequisites

Make sure the following are installed on your system before proceeding:

| Requirement | Notes |
|---|---|
| Python 3.11+ | Required to run the FastAPI backend |
| Git | For cloning the repository |
| PostgreSQL | Primary database |
| Google Chrome | Required for Playwright automation |
| VS Code *(recommended)* | For development and debugging |

---

## 2. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd resuai
```

---

## 3. Create & Activate a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## 5. PostgreSQL Setup

Install PostgreSQL and create the application database:

```sql
CREATE DATABASE resuai;
```

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/resuai
GROQ_API_KEY=YOUR_GROQ_API_KEY
JWT_SECRET_KEY=CHANGE_ME
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ Replace all placeholder values with your actual credentials before running the app.

---

## 6. Google Cloud Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Gmail API** and **Google Calendar API**.
4. Create **OAuth Desktop credentials**.
5. Download the generated `credentials.json` file.
6. Place it inside the `credentials/` directory:

```
credentials/
    credentials.json
```

---

## 7. Gmail Authentication

Start the application:

```bash
uvicorn app.main:app --reload
```

A browser window will open automatically. Follow these steps:

1. Sign in with your Gmail account.
2. Grant the requested **Gmail** and **Calendar** permissions.

A `token.pickle` file will be created automatically once authentication succeeds.

> 🔁 If OAuth scopes change later, delete `token.pickle` and re-authenticate.

---

## 8. RecruitSage Login

Run the login script once to authenticate with RecruitSage:

```bash
python login_recruitsage.py
```

The authenticated browser session will be saved and reused for future scraping operations.

---

## 9. Database Initialization

**Option A — Using SQLAlchemy `create_all()`:**

Simply start the application; tables will be created automatically.

**Option B — Using Alembic migrations:**

```bash
alembic upgrade head
```

---

## 10. Run the Application

```bash
uvicorn app.main:app --reload
```

Once running, open the interactive Swagger API docs at:

```
http://127.0.0.1:8000/docs
```

---

## 11. End-to-End Workflow

The complete placement automation pipeline runs as follows:

1. **Upload Resume** — user uploads their resume via the API.
2. **Resume Parsing** — resume content is automatically extracted and parsed.
3. **Gmail Monitoring** — the scheduler periodically checks Gmail for new emails.
4. **Email Storage** — new placement-related emails are saved to the database.
5. **LangGraph Processing** — LangGraph classifies and processes the email.
6. **RecruitSage Scraping** — the relevant RecruitSage job page is scraped.
7. **Job Parsing** — the scraped content is parsed into structured data using Groq.
8. **Job Storage** — the parsed job details are stored in the database.
9. **ATS Matching** — the job is matched against the uploaded resume(s).
10. **Calendar Sync** — application deadlines are synced to Google Calendar.

---

## 12. Common Issues

| Issue | Resolution |
|---|---|
| Gmail login repeats every run | Delete `token.pickle` and re-authenticate. |
| Calendar events missing | Ensure the Calendar API is enabled, then delete `token.pickle` and re-authenticate. |
| Playwright cannot access RecruitSage | Re-run `python login_recruitsage.py` to refresh the session. |
| Groq Error 413 | The prompt exceeds the token limit — reduce or chunk the scraped page content before sending it to the LLM. |

---

## 13. Folder Structure

```
resuai/
├── app/
├── credentials/
│   └── credentials.json
├── tokens/
│   └── token.pickle
├── playwright/
├── .env
├── requirements.txt
├── login_recruitsage.py
└── README.md
```

---

## 14. Tech Stack

- **FastAPI** — backend web framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM layer
- **LangGraph** — agentic workflow orchestration
- **LangChain** — LLM tooling and integration
- **Groq LLM** — language model for classification and parsing
- **Playwright** — browser automation for RecruitSage
- **APScheduler** — scheduled Gmail polling
- **Gmail API** — email monitoring
- **Google Calendar API** — deadline synchronization

---

## Author

**Akshat Bhatnagar**
