# Contest Platform Frontend

Next.js frontend for the contest platform.

## Local Development (Recommended)

Run the full stack from the repo root so frontend, FastAPI, Judge0, Postgres, and Redis are wired together correctly.

```bash
docker compose up --build
```

After startup:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:80`
- Judge0 API: `http://localhost:2358`
- Adminer: `http://localhost:8080`

The frontend container uses Yarn 4 PnP files from this folder (`.pnp.cjs`, `.pnp.loader.mjs`, `.yarn/`).

## Frontend-Backend URL Contract

The app resolves API URLs by runtime context:

- Browser requests use `NEXT_PUBLIC_API_BASE_URL`.
- Server-side requests use `INTERNAL_API_BASE_URL` when available.

In Docker compose these are set to:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost:80`
- `INTERNAL_API_BASE_URL=http://fastapi-starter:80`

## Frontend-Only Development

If you want to run only the frontend process:

```bash
yarn dev --hostname 0.0.0.0 --port 3000
```

Set API base URL as needed, for example:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:80
```
