# BizFlow

A production-oriented multi-tenant SaaS platform for enterprise project, task and
team management, built with React, TypeScript, Django REST Framework, PostgreSQL
and Redis — featuring JWT authentication, RBAC authorization, analytics, audit
logging, automated testing and CI/CD.

## Status

Work in progress — built incrementally, part by part. See the roadmap below.

## Stack

- **Frontend**: React, TypeScript, Vite, React Router, Tailwind CSS, Axios, Recharts, React Hook Form, Zod
- **Backend**: Python, Django, Django REST Framework, JWT (SimpleJWT), Celery, Redis
- **Database**: PostgreSQL
- **Docs**: Swagger / OpenAPI, UML & architecture diagrams

## Project structure

```
bizflow/
├── frontend/       React + TypeScript SPA
├── backend/        Django REST API (apps: authentication, companies, users,
│                    projects, tasks, notifications, reports, audit)
├── docs/           Architecture, database and API documentation
└── .github/        CI/CD workflows
```

## Getting started (development, no Docker)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp ../.env.example .env      # fill in real values
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

PostgreSQL must be running locally. Create the database and user once:

```sql
CREATE USER bizflow_user WITH PASSWORD 'your-password';
CREATE DATABASE bizflow_db OWNER bizflow_user;
GRANT ALL PRIVILEGES ON DATABASE bizflow_db TO bizflow_user;
```

## Roadmap

Built in this order, each part committed and pushed separately:

1. Repo scaffolding
2. Backend base (Django + DRF + PostgreSQL)
3. Company model (multi-tenant foundation)
4. Authentication (JWT)
5. RBAC + strict tenant isolation
6. Projects module
7. Tasks module (Kanban)
8. Comments & notifications
9. Frontend base (auth flows)
10. Frontend — Projects/Tasks UI + Kanban drag & drop
11. Dashboard & analytics
12. Audit logs
13. Reports & export (PDF/Excel/CSV)
14. Tests (backend & frontend)
15. CI/CD (GitHub Actions)
16. Simulated SaaS subscription plans
17. (Stretch) AI assistant & predictions

## License

See [LICENSE](LICENSE).
