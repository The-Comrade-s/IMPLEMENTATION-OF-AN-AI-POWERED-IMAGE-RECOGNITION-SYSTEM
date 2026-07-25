# Deployment Guide (Streamlit Community Cloud)

## Important limitation: storage is local, not cloud-native

This project uses **SQLite** and stores uploaded/annotated images on the
**local filesystem** (`uploads/`, `history/`). That's appropriate for a
final-year project demo and for a single-instance deployment, but
Streamlit Community Cloud uses an **ephemeral disk** — files (including
the database) can be wiped whenever the app restarts, sleeps, or
redeploys. Treat every deployed instance as a live demo environment, not
permanent storage: keep a local copy of anything you care about (e.g.
periodically download a database backup from **Database Management**
as admin).

For a production system beyond a course project, migrate to a managed
Postgres database and object storage (e.g. S3) — the codebase already
isolates all data access behind `database/db.py` and `services/*.py`,
so this is a swap of the connection string and the file-save calls in
`services/image_service.py`, not a rewrite.

## Deploying to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a
   new app, pointing it at `app.py` on your default branch.
3. Streamlit Cloud automatically installs `requirements.txt` and the
   system packages listed in `packages.txt` (needed for OpenCV).
4. In the app's **Settings → Secrets**, add:
   ```toml
   SECRET_KEY = "a-long-random-string"
   SESSION_TIMEOUT_MINUTES = "60"
   LOG_LEVEL = "INFO"
   ```
5. Click **Deploy**. First load will download YOLO model weights
   automatically — this can take a minute or two the very first time.
6. Once deployed, register an account, then promote it to admin (see
   `docs/INSTALLATION.md`) so you have full access to the admin panel
   on the live instance.

## Environment Variables Reference

| Variable | Purpose | Example |
|---|---|---|
| `APP_NAME` | Display name in headers/tab title | `AI-Powered Image Recognition System` |
| `SECRET_KEY` | Session/security salt | long random string |
| `SESSION_TIMEOUT_MINUTES` | Idle session timeout | `60` |
| `LOG_LEVEL` | File logging verbosity | `INFO` |

## Pre-Deployment Checklist

- [ ] `SECRET_KEY` set to a real random value (not the `.env.example` default)
- [ ] `requirements.txt` installs cleanly in a fresh virtual environment
- [ ] `packages.txt` present so Streamlit Cloud installs `libgl1`/`libglib2.0-0`
      for OpenCV
- [ ] At least one admin account created (see `docs/INSTALLATION.md`)
- [ ] Comfortable that `database/`, `uploads/`, and `history/` are
      ephemeral on this host — back up anything you need to keep
