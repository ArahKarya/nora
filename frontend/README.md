# NORA Frontend

Next.js 14 (App Router, TS, Tailwind) chat UI multi-tenant untuk NORA — Network Oracle RAG.

## Tema
WHITE + NAVY `#0F3460` + TEAL `#16C79A`. Flat, sudut tajam, heading UPPERCASE, label monospace.

## Setup
```bash
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev                   # http://localhost:3000
```

Dev command: `npm run dev` (port 3000).
Build: `npm run build` lalu `npm start`.

## Env
- `NEXT_PUBLIC_API_URL` — base backend (default `http://localhost:8010`).

## Routes
- `/login`, `/register` — auth card.
- `/` — app shell (terproteksi; redirect ke `/login` jika `me()` 401).

## Backend contract
- `POST /api/auth/register {email,password}`
- `POST /api/auth/login -> {access_token,user}`
- `GET /api/auth/me -> {id,email}`
- `GET /api/topics -> [{id,slug,name,description,count}]`
- `POST /api/query {topic_id,message,session_id?} -> {answer,confidence,flag,verifier_verdict,sources[],query_id,session_id}`

Auth = httpOnly cookie (fetch pakai `credentials: 'include'`).

## Docker
```bash
docker build --build-arg NEXT_PUBLIC_API_URL=http://api:8010 -t nora-frontend .
docker run -p 3000:3000 nora-frontend
```
