# Almo Frontend (Vite + React + Clerk)

Quick starter that uses Clerk for authentication and calls a Django REST API.

Setup

1. Copy the env example:

```bash
cp .env.example .env
# set VITE_CLERK_PUBLISHABLE_KEY in .env
```

2. Install dependencies and run

```bash
npm install
npm run dev
```

App files

- `src/App.jsx` — main app wrapped in `ClerkProvider` and routing
- `src/pages/Dashboard.jsx` — protected page that fetches `/api/protected-data/` with `Authorization: Bearer <token>`
- `src/pages/Public.jsx` — public page that fetches `/api/public-data/`
- `src/clerk-setup.js` — placeholder for the `VITE_CLERK_PUBLISHABLE_KEY`

Backend

Run your Django backend on `http://localhost:8000` with routes `/api/public-data/` and `/api/protected-data/`.
