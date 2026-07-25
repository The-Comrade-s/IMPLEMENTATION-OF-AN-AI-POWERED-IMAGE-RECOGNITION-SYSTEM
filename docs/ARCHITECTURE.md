# Architecture & Database Schema

## Layered Architecture

```
UI layer (components/*.py, app.py)
   |  Streamlit widgets, layout, session_state -- no business logic
   v
Service layer (services/*.py)
   |  Validation, orchestration, transactions -- no Streamlit imports
   v
AI layer (ai/yolo_service.py)
   |  Model loading/caching, inference, annotation drawing
   v
Data layer (database/db.py, database/models.py)
      SQLAlchemy engine/session, ORM models, SQLite file
```

Rule followed throughout: **services never import `streamlit`**, and
**UI components never talk to the database directly** -- they always go
through a service function. This is what makes the business logic
testable without a running Streamlit process (see `tests/test_core_logic.py`).

## Folder Structure

```
airs/
├── app.py                       # Entry point, routing, session bootstrap
├── config/config.py             # Settings loaded from .env
├── database/
│   ├── db.py                    # Engine, session factory, init_db()
│   └── models.py                # User, Image, DetectionResult, UserSettings,
│                                 # Notification, SystemLog
├── services/                    # Business logic (DB-aware, Streamlit-free)
│   ├── auth_service.py          # Register/login/password change
│   ├── image_service.py         # Upload validation, detection storage, history
│   ├── analytics_service.py     # Chart data aggregation queries
│   ├── report_service.py        # CSV/Excel/PDF report generation
│   ├── settings_service.py      # Per-user preferences + notifications
│   ├── profile_service.py       # Name/avatar updates
│   ├── admin_service.py         # User/image management, backups, stats
│   ├── ai_management_service.py # Global AI model/threshold config
│   └── audit_service.py         # System-wide audit log writes/reads
├── ai/yolo_service.py           # YOLOv11 loading, inference, box drawing
├── components/                  # Streamlit UI, one file per page/section
│   └── admin/                   # Admin-only pages + role guard
├── utils/                       # logger.py, validators.py
├── css/style.css                # Custom styling
├── tests/test_core_logic.py     # Unit tests for DB-free logic
└── docs/                        # This documentation set
```

## Database Schema

```
users
|-- id (PK)
|-- full_name, email (unique), password_hash, role, is_active
|-- created_at, last_login, avatar_path
`-- 1--* images, 1--1 user_settings, 1--* notifications

images
|-- id (PK), user_id (FK -> users.id)
|-- original_filename, stored_path, annotated_path
|-- file_size_bytes, width, height, image_format
|-- uploaded_at, processing_time_ms, object_count
|-- confidence_threshold, model_name
`-- 1--* detection_results

detection_results
|-- id (PK), image_id (FK -> images.id)
|-- class_name, confidence
`-- x_min, y_min, x_max, y_max, box_color

user_settings
|-- id (PK), user_id (FK -> users.id, unique)
`-- theme, default_confidence, default_model, export_format, notifications_enabled

notifications
|-- id (PK), user_id (FK -> users.id)
`-- category, message, is_read, created_at

system_logs
|-- id (PK), user_id (FK -> users.id, nullable)
`-- action, details, level, created_at
```

All tables are created automatically by `database.db.init_db()`, called
once at application startup -- no manual migrations are required. Later
phases only ever *added* nullable columns or new tables; no AIRS-001
column was renamed or removed.

## AI Workflow

1. `components/recognition_page.py` collects an uploaded file and
   user-chosen model/confidence.
2. `services/image_service.process_and_store_detection()`:
   - validates and (if oversized) downscales the image,
   - calls `ai/yolo_service.run_detection()`,
   - saves the original and annotated images to disk,
   - persists an `Image` row plus one `DetectionResult` row per object.
3. `ai/yolo_service.load_model()` is wrapped in `st.cache_resource`, so
   the YOLO model is loaded into memory once per process, not on every
   Streamlit rerun.
