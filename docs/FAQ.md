# Frequently Asked Questions

**Q: Does this run without internet access?**
A: The app itself runs fully offline once YOLO model weights are cached
locally. The first detection with a given model size requires internet
access to download that model's weights.

**Q: Can I use my own trained YOLO weights?**
A: Yes. Place your `.pt` file in the project root (or provide a path),
add an entry to `AVAILABLE_MODELS` in `ai/yolo_service.py`, and select
it from AI Management (as admin) or Detection Settings (as a user).

**Q: Why SQLite instead of Postgres/MySQL?**
A: SQLite requires no separate server, which keeps setup to a single
`pip install` for a course project and live demo. See
`docs/DEPLOYMENT.md` for notes on migrating to Postgres for real
production use.

**Q: Is there rate limiting on login attempts?**
A: Failed logins are logged to the audit trail (System Logs, as admin),
but there is no automatic lockout after N failed attempts in this
version — that would be a reasonable future enhancement (see README).

**Q: Can two people use the same account at once?**
A: Sessions are per-browser-session via `st.session_state`, so this
works, but detection history and settings are shared per user account,
not per session.

**Q: Where are uploaded images stored?**
A: Originals in `uploads/`, annotated results in `history/`, both on
local disk relative to the project root. See `docs/DEPLOYMENT.md` for
the implications of ephemeral storage on cloud hosts.

**Q: How do I change the maximum upload size?**
A: Admins can set a *displayed* limit in System Settings, but the
enforced limit is `services/image_service.MAX_FILE_SIZE_BYTES` (15 MB
by default) — change that constant and redeploy to raise the real cap.
