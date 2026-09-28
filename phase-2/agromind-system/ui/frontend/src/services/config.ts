// The frontend never talks to the model server or the RAG server directly.
// It only ever calls this app's own backend proxy, which is the one place
// MODEL_API_URL / RAG_API_URL are configured (see /server).
//
// - In development, leave VITE_API_BASE_URL unset: Vite proxies /api to the
//   backend (see vite.config.ts).
// - In production, set VITE_API_BASE_URL to wherever the backend proxy is
//   deployed, e.g. https://api.agromind.example.com/api.
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || '/api';
