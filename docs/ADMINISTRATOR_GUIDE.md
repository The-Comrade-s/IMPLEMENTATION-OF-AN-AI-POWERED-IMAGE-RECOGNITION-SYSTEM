# Administrator Guide

Admin-only pages appear in the sidebar automatically once your account's
role is `admin` (see `docs/INSTALLATION.md` for how to promote an
account). Non-admin accounts never see these options and are blocked at
the page level if they navigate to an admin URL directly.

## Admin Dashboard

System-wide metrics: total/active users, images processed, objects
detected, database size, storage used, average processing time, and the
currently active AI model.

## User Management

- Search users by name or email.
- **Activate/Deactivate** — deactivated users cannot log in.
- **Make admin / Make user** — promote or demote roles.
- **Reset PW** — generates a temporary password, shown once on screen.
  Share it with the user through a secure channel; they should change
  it immediately after logging in (Settings → Password).
- **Delete** — permanently removes the account and, via cascade, their
  images/detections/settings/notifications.

You cannot deactivate, demote, or delete your own currently logged-in
account from this screen.

## Image Management

Browse every image uploaded system-wide, search by filename or
uploader email, and delete any image (removes both the database record
and the files on disk).

## AI Management

- View the active YOLO model and default confidence threshold.
- Switch model size (Nano/Small/Medium/Large) — larger models are more
  accurate but slower and use more memory.
- **Reload Model** clears the cached model instance so the new
  configuration takes effect immediately.
- **Test Model** runs a lightweight health check.

## System Logs

A searchable, filterable audit trail covering registrations, logins
(including failed attempts), password changes, admin actions (role
changes, deletions, resets), AI configuration changes, and database
operations. Export to CSV for record-keeping.

## Database Management

- View database size and record counts.
- **Create Backup Now** — copies the SQLite file into `database/backups/`.
- **Run Integrity Check** — runs SQLite's `PRAGMA integrity_check`.
- **Restore** — replaces the live database with a selected backup.
  Restart the app afterward so all connections pick up the restored file.
- Scheduled/automatic backups aren't built into Streamlit itself (it has
  no background scheduler); run the backup action via an external cron
  job or task scheduler that calls into this page's underlying service
  (`services/admin_service.backup_database`) on a schedule if you need
  unattended backups.

## System Settings

Application name, max upload size, allowed file types, session timeout,
and logging level. Some changes (like logging level) apply after an
application restart.

## Security Notes

- All admin actions are written to the System Logs audit trail.
- Passwords are always bcrypt-hashed; the admin-issued temporary
  password is shown once and is not stored in plain text anywhere.
- Only users with `role = "admin"` can reach admin pages or call the
  underlying admin service functions from the UI layer.
