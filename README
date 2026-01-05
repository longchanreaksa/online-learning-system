# Online Learning System

A lightweight platform for creating courses, lessons, quizzes and tracking student progress.

## Features
- Roles: admin, instructor, student
- Course & lesson management
- Quizzes with basic auto-grading
- Progress tracking and simple analytics
- File/video attachments and rich text

## Tech stack (example)
- Backend: Node.js / Django
- Frontend: React / Vue
- Database: PostgreSQL / MySQL
- Auth: JWT (or replace as used)
- Optional: Docker, S3-compatible storage

## Quickstart (local)
1. Clone
```bash
git clone https://github.com/longchanreaksa/online-learning-system.git
cd online-learning-system
```
2. Install (example)
```bash
# backend
cd backend && npm install
# frontend
cd ../frontend && npm install
```
3. Environment
```bash
cp .env.example .env
# set DATABASE_URL, JWT_SECRET, PORT, etc.
```
4. Database & migrations
```bash
createdb online_learning
cd backend
npm run migrate    # or appropriate migrate command
```
5. Run (development)
```bash
# backend
npm run dev
# frontend (separate terminal)
cd ../frontend && npm run dev
# open http://localhost:3000 (or configured PORT)
```

## Testing
Run unit/integration tests:
```bash
# from repo root or appropriate subdir
npm test
```

## Docker (optional)
Build and start with docker-compose:
```bash
docker-compose up --build
```
Ensure env vars are provided to docker-compose or via .env.

## Deployment notes
- Store secrets in env vars or a secret manager (do NOT commit .env)
- Use managed DB (RDS / Cloud SQL) and object storage (S3)
- Serve static assets via CDN; enable HTTPS and health checks

## Project layout (high level)
- /backend — API and server code
- /frontend — client app
- /docs — design & screenshots
- /migrations — DB migrations
- docker-compose.yml, Dockerfile, README

## Contributing
1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit, push, open a PR; include tests and update docs for major changes

## License
- MIT (add a LICENSE file at the repository root or replace with your chosen license)

## Contact
- Maintainer: [@longchanreaksa](https://github.com/longchanreaksa)
- Repo: https://github.com/longchanreaksa/online-learning-system
