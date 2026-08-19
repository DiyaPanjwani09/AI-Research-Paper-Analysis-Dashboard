# Single-container Dockerfile for Render deployment
# Builds the React frontend, serves it with nginx, and runs the FastAPI backend

# ---- Stage 1: Build React frontend ----
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python backend + nginx runtime ----
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies: nginx + build tools for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY backend/ ./backend/
WORKDIR /app/backend

# Frontend static build -> served by nginx
COPY --from=frontend-build /app/frontend/build /app/static
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p uploads vector_db

# Render routes to $PORT; nginx listens on $PORT and proxies /api to uvicorn on 8001
EXPOSE 8000
CMD ["sh", "-c", "envsubst '${PORT}' < /etc/nginx/conf.d/default.conf > /tmp/default.conf && cat /tmp/default.conf > /etc/nginx/conf.d/default.conf && nginx && uvicorn main:app --host 0.0.0.0 --port 8001"]