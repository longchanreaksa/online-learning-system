# Online Learning System

A lightweight online learning platform built with Django (MVT pattern) and plain HTML/CSS for the frontend. It provides basic course and lesson management, quizzes with auto-grading, user roles, and student progress tracking. This project is intended to be simple to run locally using SQLite and does not use Docker or any frontend framework.

---

## Features
- User roles: `admin`, `instructor`, `student`
- Course and lesson creation / management
- Progress tracking per student and course
- File/video attachments and rich-text content in lessons
- Simple analytics (course completion, quiz scores)
- Server-rendered frontend with HTML and CSS

---

## Tech stack
- Backend: Python, Django (Model-View-Template — MVT)
- Frontend: Django templates, HTML, CSS, and JavaScript
- Database (development): SQLite
- Auth: Django auth JWT

---

## Quickstart (local development)

1. Clone the repository
```bash
git clone https://github.com/longchanreaksa/online-learning-system.git
cd online-learning-system
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies
```bash
# If requirements.txt is at repo root
pip install -r requirements.txt

# or, if the Django project is inside `backend` and requirements there:
cd backend
pip install -r requirements.txt
cd ..
```

4. Environment variables
Copy example env (if provided) and edit:
```bash
cp .env.example .env
# open .env and set SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.
```

If you don't use an .env file, ensure the settings module or environment provides:
- SECRET_KEY (do NOT commit this)
- DEBUG (True for local)
- ALLOWED_HOSTS (e.g. localhost, 127.0.0.1)
- Any other custom settings your project expects

5. Database setup & migrations
```bash
# From the Django project folder (where manage.py is)
python manage.py migrate
```

6. Create a superuser (admin)
```bash
python manage.py createsuperuser
# follow prompts
```

7. Run the development server
```bash
python manage.py runserver
# Open http://127.0.0.1:8000
```

---

## Environment / configuration

Example minimal `.env` entries (if you use django-environ or similar):
```
SECRET_KEY=replace-with-a-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
# If you later move to PostgreSQL:
# DATABASE_URL=postgres://user:password@host:port/dbname
```

Default development settings typically use SQLite:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Important: Never commit production SECRET_KEY or .env files to source control.

---

If you'd like, I can:
- tailor this README to your exact folder structure (I can update paths/commands if Django is at `/backend` or repo root),
- add a sample `.env.example`,
- or create a `production.md` with step-by-step deployment instructions for a specific host (Heroku, DigitalOcean, AWS).
