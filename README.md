# AI-Powered Image Recognition System (AIRS)

A production-quality final-year Computer Science project: a Python +
Streamlit web application for AI-powered object detection, built with
YOLOv11, SQLite, and a full multi-user + admin feature set.

Built in five phases (AIRS-001 → AIRS-005), each extending the last
without breaking existing functionality. See `docs/` for full
documentation.

## Feature Summary

**Core (AIRS-001)**
Landing page, registration/login (bcrypt-hashed passwords), session
management, sidebar navigation, dashboard shell, settings shell, custom
CSS, rotating file logging, centralized error handling.

**AI Engine (AIRS-002)**
Drag-and-drop image upload with validation, YOLOv11 object detection
(selectable model size + confidence threshold), bounding boxes with
labels/confidence, annotated-image/CSV/JSON downloads, detection
history with search and delete.

**Analytics & User Features (AIRS-003)**
Dashboard driven by real detection data, interactive Plotly analytics
(top objects, category breakdown, daily/monthly activity, confidence
distribution, processing-time trend), profile editing with avatar
upload, per-user preferences, CSV/Excel/PDF report export, in-app
notifications.

**Admin Panel (AIRS-004)**
Role-based access control, admin dashboard with system-wide metrics,
user management (activate/deactivate, promote/demote, reset password,
delete), image management, AI model configuration, searchable system
audit logs, database backup/restore/integrity check, system settings.

**Hardening & Deployment (AIRS-005)**
Full static audit (every module compiles and every cross-module
function reference was verified to exist), a documented and fixed
SQLite write-lock issue in the audit-logging path, a pytest-based unit
test suite for dependency-light logic, complete documentation set,
`requirements.txt`, and deployment configuration for Streamlit
Community Cloud.

## Project Structure

```
airs/
├── app.py                      # Entry point (streamlit run app.py)
├── config/config.py            # Settings from .env
├── database/                   # SQLAlchemy models + session management
├── services/                   # Business logic, no Streamlit imports
├── ai/yolo_service.py          # YOLOv11 inference engine
├── components/                 # Streamlit UI, incl. components/admin/
├── utils/                      # Logging, validation
├── css/style.css               # Custom styling
├── tests/test_core_logic.py    # Unit tests
├── docs/                       # Installation, user/admin guides, etc.
├── .streamlit/config.toml      # Streamlit runtime config
├── packages.txt                # System deps for Streamlit Cloud
└── requirements.txt
```

Full architecture and database schema: `docs/ARCHITECTURE.md`.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit SECRET_KEY
streamlit run app.py
```

Register an account from the homepage, then log in. To create an admin
account, see `docs/INSTALLATION.md`.

## Documentation

| Doc | Purpose |
|---|---|
| `docs/INSTALLATION.md` | Local setup, first use, creating an admin |
| `docs/USER_MANUAL.md` | How to use every end-user feature |
| `docs/ADMINISTRATOR_GUIDE.md` | How to use every admin feature |
| `docs/ARCHITECTURE.md` | Layered architecture + full DB schema |
| `docs/DEPLOYMENT.md` | Streamlit Community Cloud deployment |
| `docs/TROUBLESHOOTING.md` | Common issues and fixes |
| `docs/FAQ.md` | Frequently asked questions |
| `docs/PROJECT_REPORT.md` | Abstract, objectives, methodology, results, limitations — for the written report |

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

`tests/test_core_logic.py` covers input validation, upload validation,
image-resizing, and the detection-drawing logic without needing a
database or a downloaded model. Full end-to-end flows (registration,
detection, admin actions) should be verified manually against a running
instance using the checklist in `docs/PROJECT_REPORT.md`.

## Known Limitations

- SQLite + local disk storage — not designed for multi-instance
  deployment (see `docs/DEPLOYMENT.md`).
- No email-based password recovery (admin-assisted reset only).
- No automatic login-attempt rate limiting.

See `docs/PROJECT_REPORT.md` → "Limitations" and "Future Work" for the
complete list.
