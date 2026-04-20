# REST API Integration and Backend Workflow

A production-ready full-stack portfolio project that demonstrates how to integrate a third-party REST API, validate and normalize external data, add backend workflow logic, cache responses, and present the result in a polished business dashboard.

The example product is a **Repository Activity Dashboard**. The FastAPI backend integrates with the public GitHub REST API, processes repository, issue, contributor, and activity data, then exposes stable internal endpoints consumed by a React dashboard.

## Business Scenario

Many client projects need more than a frontend calling a third-party API directly. They need a backend layer that can:

- hide third-party API complexity from the UI
- normalize inconsistent or changing external payloads
- validate data before it reaches business workflows
- cache expensive requests to improve speed and reduce rate-limit pressure
- handle failures gracefully with friendly errors or stale cached data
- expose clean internal endpoints aligned with product needs

This project is designed to showcase freelance services such as REST API integration, backend workflow development, third-party system integration, data normalization, and troubleshooting API-driven applications.

## External API

The backend uses the [GitHub REST API](https://docs.github.com/en/rest) public endpoints:

- repository details
- issues
- contributors
- recent repository events

No authentication is required for the default demo, but adding `GITHUB_TOKEN` increases rate limits and is recommended for heavier use.

## What The Backend Adds

Instead of passing raw GitHub JSON to the frontend, the backend provides a clean internal data contract:

- Pydantic schemas validate GitHub responses
- service logic normalizes repository, issue, contributor, and activity records
- business-friendly metrics summarize stars, forks, watchers, issue volume, contributor activity, and top language
- issue records are filtered, de-duplicated from pull requests, aged, labeled, and assigned a simple priority
- contributor data is aggregated across tracked repositories
- recent GitHub event types are converted into dashboard-friendly labels
- an in-memory TTL cache reduces repeated GitHub calls
- stale cached data can be returned when GitHub is temporarily unavailable
- API errors are returned as structured friendly payloads

## Architecture

```text
backend/
  app/
    api/routes/          FastAPI route layer
    clients/             GitHub REST API client with timeout/retry handling
    core/                configuration and cache utilities
    schemas/             external GitHub and internal dashboard schemas
    services/            normalization, aggregation, filtering, transformations
    main.py              FastAPI app setup

frontend/
  src/
    api/                 typed dashboard API client
    types.ts             frontend data contracts
    App.tsx              dashboard UI, filtering, states, responsive views
```

## Backend Endpoints

Base URL: `http://127.0.0.1:8000`

- `GET /health`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/repos`
- `GET /api/dashboard/issues`
- `GET /api/dashboard/contributors`
- `GET /api/dashboard/activity`

Optional query examples:

- `/api/dashboard/repos?search=fastapi`
- `/api/dashboard/issues?state=open&priority=high&limit=20`
- `/api/dashboard/activity?repo=fastapi/fastapi`
- `/api/dashboard/summary?repositories=fastapi/fastapi,encode/httpx`

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional environment variables:

```bash
set GITHUB_TOKEN=your_github_token
set DASHBOARD_REPOSITORIES=fastapi/fastapi,encode/httpx,pydantic/pydantic,vitejs/vite
set CACHE_TTL_SECONDS=300
set STALE_CACHE_TTL_SECONDS=1800
set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite app runs at `http://localhost:5173` and expects the backend at `http://127.0.0.1:8000`.

To point the frontend to a different backend:

```bash
set VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Production Build

Frontend:

```bash
cd frontend
npm run build
```

Backend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deployment Approach

A typical deployment would host the FastAPI backend and static frontend separately:

- Backend on Render, Railway, Fly.io, Azure App Service, AWS ECS, or a VPS
- Frontend on Vercel, Netlify, Cloudflare Pages, or behind the same reverse proxy
- Set `GITHUB_TOKEN` as a backend secret
- Set `VITE_API_BASE_URL` during frontend build
- Restrict `CORS_ORIGINS` to the deployed frontend domain
- Replace the in-memory cache with Redis if multiple backend instances are used

## Portfolio Positioning

This project is intentionally framed as a client-ready integration workflow:

- **REST API integration:** external GitHub API calls are isolated in a client layer
- **Backend workflow development:** service logic applies transformations, filtering, aggregation, and dashboard shaping
- **Third-party system integration:** backend absorbs third-party response details and exposes stable internal endpoints
- **Data normalization:** raw GitHub payloads become consistent internal schemas
- **Troubleshooting API applications:** retries, timeouts, rate-limit messaging, stale cache fallback, and structured errors improve reliability

The result is a believable internal dashboard that demonstrates both backend engineering and frontend product presentation.
