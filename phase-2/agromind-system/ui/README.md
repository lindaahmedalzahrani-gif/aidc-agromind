# AgroMind — Web Application

An end-user demo interface for AgroMind: upload a photo of a crop or plant and
get an AI diagnosis of the crop and any visible disease or pest, with a
follow-up "Ask AgroMind" assistant.

This project is the **frontend + a thin backend proxy** only. It does not
contain any model-inference code — that lives on the GPU-served model API
and, later, the RAG API, both external to this repo.

```
Browser
   │
   ▼
AgroMind UI (frontend/, React + Vite + TypeScript)
   │  fetch('/api/diagnose'), fetch('/api/chat')
   ▼
AgroMind backend proxy (server/, Node + Express)
   ├── POST /api/diagnose  →  MODEL_API_URL   (fine-tuned vision-language model)
   └── POST /api/chat      →  RAG_API_URL     (agricultural knowledge assistant)
```

The frontend never calls the model or RAG servers directly and never hard-codes
a checkpoint name, IP, or `localhost` URL — it only ever calls its own backend
at `/api/...`. The backend is the single place `MODEL_API_URL` and
`RAG_API_URL` are configured, so pointing this app at your real infrastructure
later is an environment-variable change, not a code change.

## Project structure

```
agromind/
├── frontend/                  React + Vite + TypeScript app
│   ├── src/
│   │   ├── components/        Header, Hero, Diagnose, Chat, About, Footer
│   │   ├── i18n/               translations.ts (EN/中文 dictionary), LanguageContext
│   │   ├── services/           diagnosisService.ts, chatService.ts, config.ts
│   │   ├── types/
│   │   └── styles/              tokens.css (design system), global.css
│   └── .env.example
├── server/                    Node + Express backend proxy
│   ├── index.js                 routes: /api/diagnose, /api/chat, /api/health
│   ├── services/
│   │   ├── modelClient.js       the ONLY file that knows the model API's shape
│   │   └── ragClient.js         the ONLY file that knows the RAG API's shape
│   └── .env.example
└── package.json                convenience scripts to run both together
```

## Prerequisites

- Node.js 18 or later (uses the built-in `fetch` and `node --watch`)

## Quick start (local development)

```bash
# 1. Install dependencies for both apps
npm run install:all

# 2. Configure the backend (see "Connecting your APIs" below)
cp server/.env.example server/.env

# 3. Run both the frontend and backend together
npm run dev
```

This starts:
- the frontend at **http://localhost:5173** (Vite dev server, proxies `/api` to the backend)
- the backend at **http://localhost:8787**

Without any further configuration, the app runs fully: the diagnose panel
shows its "AgroMind is unavailable right now" state (because no model is
connected yet), and the chat panel answers with a clearly labeled mock reply.
This is intentional — it's a truthful placeholder, not a fake result.

If you'd rather run them in two separate terminals instead of using
`npm run dev`:

```bash
# terminal 1
npm --prefix frontend run dev

# terminal 2
npm --prefix server run dev
```

## Connecting your model and RAG APIs

All of this happens in **`server/.env`** — no frontend code changes needed.

1. Copy the template: `cp server/.env.example server/.env`
2. Set `MODEL_API_URL` to your deployed vLLM service's base URL (the one
   exposing an OpenAI-compatible `/v1/chat/completions` endpoint), e.g.:
   ```
   MODEL_API_URL=http://<your-service-host>:<port>
   ```
3. Once your RAG service exists, set `RAG_API_URL` the same way. Until then,
   leave it blank and `/api/chat` will keep returning mock replies.
4. Restart the backend (`npm --prefix server run dev`).

That's the entire integration. `server/services/modelClient.js` and
`server/services/ragClient.js` are the only files that build requests to
those APIs and parse their responses — if either API's request/response
shape changes later, only those two files need to change.

### Expected API shapes (adjust the two files above if yours differs)

**Model server** — OpenAI-compatible chat completions with an image, at
`POST {MODEL_API_URL}/v1/chat/completions`, returning free-text in the format
`crop, disease`. The backend parses that text into:
```json
{ "crop": "Grape", "disease": "Powdery Mildew", "is_healthy": false, "model_response": "Grape, Powdery Mildew" }
```

**RAG server** — `POST {RAG_API_URL}/chat`:
```json
// request
{ "message": "How should I manage this?", "language": "en", "context": { "crop": "Grape", "disease": "Powdery Mildew" } }
// response
{ "reply": "..." }
```

## Environment variables

**`frontend/.env`** (copy from `frontend/.env.example`)

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend proxy. Leave unset for local dev (Vite proxies `/api` automatically). Set it in production if the frontend and backend aren't on the same origin. |

**`server/.env`** (copy from `server/.env.example`)

| Variable | Purpose |
|---|---|
| `PORT` | Port the backend listens on (default `8787`). |
| `MODEL_API_URL` | Base URL of the fine-tuned model server. Empty = `/api/diagnose` returns a 503 "not connected" response. |
| `MODEL_PROMPT_EN` / `MODEL_PROMPT_ZH` | The exact prompt sent with each image, per language. |
| `RAG_API_URL` | Base URL of the RAG server. Empty = `/api/chat` returns a mock reply. |
| `ALLOWED_ORIGINS` | Comma-separated CORS allow-list for production. Empty = allow all (fine for local dev). |

## Production build

```bash
npm run build            # builds frontend/dist as static assets
npm --prefix server start  # runs the backend
```

Serve `frontend/dist` from any static host or CDN, deploy `server/` as a small
Node service, and set `VITE_API_BASE_URL` (frontend) / `MODEL_API_URL` and
`RAG_API_URL` (backend) for that environment.

## Adding a third language

Add one more top-level key to `frontend/src/i18n/translations.ts` with the
same shape as `en`/`zh`, then add a button for it in
`frontend/src/components/Header/Header.tsx`. No other file needs to change —
every string in the interface is read from this one dictionary, and model
output text is kept separate from UI translations by design.
