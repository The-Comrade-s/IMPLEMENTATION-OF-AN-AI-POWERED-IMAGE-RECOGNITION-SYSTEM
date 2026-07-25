# Installation Guide

## Prerequisites

- Python 3.12+
- pip
- ~2 GB free disk space (for YOLO model weights, once downloaded)
- Internet access on first run (to download YOLO weights automatically)

## Local Setup

```bash
# 1. Extract the project and enter its folder
cd airs

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set a real SECRET_KEY

# 5. Run the application
streamlit run app.py
```

The app opens at `http://localhost:8501`. The SQLite database and all
required tables are created automatically on first run — no manual
migration step is needed.

## First Use

1. Open the app — you'll land on the public homepage.
2. Click **Get Started** → **Create one here** to register an account.
3. Log in, then go to **Image Recognition** to upload your first image.
   The first detection will trigger an automatic download of YOLOv11
   model weights (a few seconds to a couple of minutes depending on
   your connection).

## Creating an Administrator Account

There is no seeded admin account. To promote a user to admin:

```bash
python - <<'PY'
from database.db import get_session, init_db
from database.models import User

init_db()
with get_session() as session:
    user = session.query(User).filter_by(email="you@example.com").first()
    if user:
        user.role = "admin"
        session.add(user)
        print("Promoted:", user.email)
    else:
        print("No such user — register the account first, then re-run this script.")
PY
```

Register the account through the normal UI first, then run the snippet
above with that account's email.

## Troubleshooting Installation

See `docs/TROUBLESHOOTING.md`.
