# Troubleshooting Guide

## "ModuleNotFoundError" on startup
Run `pip install -r requirements.txt` inside the active virtual
environment you're launching `streamlit run app.py` from.

## YOLO model fails to load / "Detection failed"
- Confirm internet access on first run — Ultralytics downloads model
  weights (`yolo11n.pt`, etc.) automatically the first time each size
  is used.
- Check `logs/app.log` for the full stack trace.
- As an admin, go to **AI Management → Test Model** to isolate whether
  the issue is the model itself or a specific image.

## "database is locked" errors
SQLite allows only one writer at a time. This can happen under heavy
concurrent load. Mitigations already in the codebase:
- Every database write uses a short-lived session (`get_session()`)
  that commits and closes immediately — no session is held open across
  unrelated operations.
- Audit-log writes (`record_event`) always run *after* the primary
  write's session has committed, not nested inside it.
If you still see this under load, it's a sign you've outgrown SQLite —
see `docs/DEPLOYMENT.md` for migrating to Postgres.

## Uploaded image is rejected
- Supported formats: JPG, JPEG, PNG, BMP, WEBP.
- Maximum size: 15 MB (configurable by an admin in **System Settings**,
  though the hard validation limit lives in
  `services/image_service.MAX_FILE_SIZE_BYTES` and requires a code
  change to raise).

## Large images are slow to process
Images with a longest side over 4000px are automatically downscaled
before inference (`services/image_service._resize_if_needed`) to keep
memory use and latency reasonable. If detections still feel slow,
switch to a smaller model (Nano/Small) in Detection Settings or, as an
admin, in AI Management.

## Out of memory during detection
Use a smaller YOLO model size, and/or reduce the maximum image
dimension. On constrained hosts (e.g. free-tier cloud dynos), the Nano
model is strongly recommended.

## Charts on the Analytics page are empty
Analytics need at least one completed detection. Run a detection from
**Image Recognition** first.

## Forgot password
There's no self-service "forgot password" email flow (would require an
SMTP/email service not in scope for this project). Ask an administrator
to use **User Management → Reset PW**, which issues a one-time
temporary password.

## Admin pages don't show up in the sidebar
Your account's `role` must be exactly `admin` in the `users` table. See
`docs/INSTALLATION.md` → "Creating an Administrator Account".

## Streamlit Cloud deploy fails on OpenCV import
Ensure `packages.txt` is present in the repo root — Streamlit Community
Cloud reads it automatically to install `libgl1` and `libglib2.0-0`,
both required by `opencv-python-headless` even though it's the
"headless" build.
