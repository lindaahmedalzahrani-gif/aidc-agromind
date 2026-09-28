# ============================================================
# Stage 1 - Build React/Vite frontend
# ============================================================

FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./

COPY frontend/package.json frontend/package-lock.json ./frontend/
COPY server/package.json server/package-lock.json ./server/

RUN npm install --prefix frontend
RUN npm install --prefix server

COPY frontend ./frontend
COPY server ./server

# Browser calls the Express UI backend, not FastAPI directly.
ENV VITE_API_BASE_URL=/ui-api

RUN npm --prefix frontend run build


# ============================================================
# Stage 2 - Production Express server
# ============================================================

FROM node:20-alpine

WORKDIR /app

COPY package.json ./

COPY server/package.json server/package-lock.json ./server/

RUN npm install \
    --prefix server \
    --omit=dev

COPY server ./server

COPY --from=build \
    /app/frontend/dist \
    ./frontend/dist

ENV NODE_ENV=production
ENV PORT=8787

EXPOSE 8787

CMD ["node", "server/index.js"]
