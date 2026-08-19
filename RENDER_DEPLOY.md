# Render deployment guide

This repository is ready to deploy with a Render Blueprint. The Blueprint creates:

- `ai-research-frontend`: React static site
- `ai-research-backend`: FastAPI web service
- `ai-research-db`: Render Postgres database

## Deploy with Blueprint

1. Push these files to GitHub.
2. Open Render and choose **New > Blueprint**.
3. Connect `DiyaPanjwani09/AI-Research-Paper-Analysis-Dashboard`.
4. Select the repository and keep the detected `render.yaml`.
5. Click **Apply**.

Render will build the backend, frontend, and database together. The frontend `REACT_APP_API_URL` is wired to the backend's generated Render URL, and the backend `ALLOWED_ORIGINS` is wired to the frontend's generated Render URL.

## After deploy

1. Open the backend service and check `/health`.
2. Open the frontend static site URL.
3. Upload a small PDF first, because the first ML request can be slow while models initialize.

## Notes

- The Blueprint uses Render Free instances. Free Postgres databases expire after 30 days, and free web services can sleep when idle.
- Uploads and FAISS indexes are stored in `/tmp` on the backend. They are fine for demos, but they will not persist across restarts.
- If the backend fails with memory errors while loading ML models, upgrade `ai-research-backend` from `free` to a paid instance type in Render.
