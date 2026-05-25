# Carbonflow ESG Platform

A Django REST backend and React frontend prototype for ingesting emissions-related data from SAP, utility portals, and corporate travel.

## What this repo contains
- `backend/`: Django app with ingestion models, CSV parsing, review workflow, and REST APIs.
- `frontend/`: React + Vite review dashboard for uploading files, fetching travel records, and approving rows.
- `MODEL.md`, `DECISIONS.md`, `TRADEOFFS.md`, `SOURCES.md`: assignment documentation.
- `samples/`: example CSV sources for SAP fuel/procurement and utility electricity billing.

## Local setup

### Backend

```bash
cd /workspaces/carbonflow-esg-platform/backend
python3 -m pip install -r ../requirements.txt
python3 manage.py migrate
python3 manage.py runserver 8000
```

### Frontend

```bash
cd /workspaces/carbonflow-esg-platform/frontend
npm install
npm run dev
```

The frontend proxies `/api` to `http://localhost:8000`.

## Deployment

- A `Dockerfile` and `render.yaml` are included for Render deployment.
- The app listens on port `8000` by default and serves the React build from Django's static assets.
- To deploy on Render, connect this repo and use the `render.yaml` service definition.
  - In Render, create a new Web Service from the repo `diyaitis/carbonflow-esg-platform` on branch `main`.
  - Choose Docker as the runtime and use `./Dockerfile` as the Dockerfile path.
  - Set environment variables:
    - `DJANGO_DEBUG=0`
    - `DJANGO_SECRET_KEY=<your-secret>`
    - `DATABASE_URL=<render-postgres-url>`
  - Add a PostgreSQL database under the same project, then copy its connection URL to Render's `DATABASE_URL`.
  - You can leave `PORT` unset because the Docker runtime passes it automatically to the container.
- In production, use `DATABASE_URL` with Postgres. The app falls back to SQLite only when no `DATABASE_URL` is set, which is not recommended on Render.

## Live preview

- The current live preview URL from the GitHub Codespace is:
- `https://jubilant-bassoon-6j5q9q665pj3xr65-8000.app.github.dev`

## Health and validation

- Health endpoint: `/api/health/` returns `{"status":"ok"}`
- Input validation:
	- Uploads are limited to 10 MB and must be CSV files.
	- The ingestion API validates `tenant_id` and `source_type`.
	- The serializer enforces that either `quantity` or `normalized_quantity` is present.

## Quick validation commands

Run sample ingests locally via Django management command:

```bash
cd backend
python3 manage.py run_sample_ingests
```

## Quick test data
- `samples/sap-fuel-sample.csv`
- `samples/utility-electricity-sample.csv`

## Notes
- Default tenant `Example Client` is created automatically by a migration.
- Travel ingestion is simulated via a mocked travel API fetch for prototype purposes.
