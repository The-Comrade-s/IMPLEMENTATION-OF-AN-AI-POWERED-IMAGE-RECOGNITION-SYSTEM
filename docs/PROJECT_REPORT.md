# Project Report Support Material

Original content to support the written final-year project report. Adapt
freely to your institution's required structure and word counts.

## Abstract

This project presents the design and implementation of an AI-Powered
Image Recognition System — a web-based application that allows users to
upload images and receive real-time object detection results, complete
with bounding boxes, class labels, and confidence scores. The system is
built entirely in Python using the Streamlit framework for its interface
and Ultralytics YOLOv11 for object detection, backed by a SQLite
database for user accounts, detection history, and system
administration. Beyond the core detection pipeline, the system provides
per-user analytics, exportable reports (CSV, Excel, PDF), and a
role-based administrator panel for user management, system monitoring,
and database maintenance. The result is a self-contained, deployable
application suitable for demonstrating a practical, end-to-end computer
vision workflow.

## Problem Statement

Manually reviewing images to catalogue or count objects within them is
slow, error-prone, and does not scale. Off-the-shelf object detection
demos, meanwhile, are typically single-purpose scripts without user
accounts, history, or any way to track detection activity over time.
There is a need for an accessible, self-hosted application that wraps a
modern object detection model in a usable interface with persistence,
multi-user support, and administrative oversight.

## Aim

To design and implement a full-stack, AI-powered image recognition web
application that is secure, usable by non-technical end users, and
maintainable by a system administrator.

## Objectives

1. Provide secure user registration, authentication, and session
   management.
2. Allow users to upload images and run object detection using a
   modern, pretrained deep learning model (YOLOv11).
3. Persist detection results and present them as searchable,
   filterable history.
4. Provide analytics and exportable reports summarizing detection
   activity.
5. Provide an administrator panel for user management, system
   monitoring, and database maintenance.
6. Package the system for straightforward local installation and cloud
   deployment.

## Scope

In scope: single-image upload and detection, per-user history and
analytics, CSV/Excel/PDF export, role-based access control (user vs
admin), system logging, database backup/restore. Out of scope: video or
real-time camera detection, custom model training/fine-tuning within
the app, multi-tenant organizations, and email-based password recovery.

## Methodology

The system was built incrementally across five phases, each verified
before the next began:

1. **Foundation** — project architecture, database schema,
   authentication, and the base UI shell.
2. **AI Engine** — YOLOv11 integration, upload/preview/detection/results
   flow, and persistence of detection results.
3. **Analytics & User Features** — dashboard metrics, charts, history
   management, profile, preferences, and report export.
4. **Administration** — role-based access control, user/image
   management, system logs, AI configuration, and database tools.
5. **Hardening** — a full-project audit, documentation, and deployment
   preparation.

This phased approach mirrors standard iterative software development
practice: each phase extended the previous one without breaking
existing functionality, which was re-verified at every stage.

## System Architecture

See `docs/ARCHITECTURE.md` for the full layered architecture diagram
and database schema. In summary: a Streamlit UI layer calls into a
Streamlit-free service layer, which in turn uses a dedicated AI layer
(YOLO inference) and a data layer (SQLAlchemy ORM over SQLite).

## Implementation Summary

- **Frontend:** Streamlit with custom CSS for a distinctive, non-default
  appearance (gradient headers, card-based layout, colour-coded badges).
- **Backend logic:** organized into single-responsibility service
  modules (auth, image processing, analytics, reporting, admin,
  settings) to keep business logic testable independent of the UI.
- **AI:** Ultralytics YOLOv11, loaded once per process via Streamlit's
  resource cache, with configurable model size and confidence
  threshold.
- **Security:** bcrypt password hashing, input validation on every
  form, and a role-based guard on every admin page.
- **Persistence:** SQLite via SQLAlchemy ORM; six tables covering
  users, images, detections, preferences, notifications, and audit
  logs.

## Testing Summary

Automated tests (`tests/test_core_logic.py`) cover input validation,
upload validation, image-resizing logic, and the detection-annotation
drawing routine — the parts of the system that don't require a live
database or network access, so they run quickly in CI. Database-backed
flows (registration, login, detection persistence, admin actions) were
verified through structured manual testing against the running
application, following the checklist below, plus a full static compile
pass over every module.

### Manual Test Checklist

- [ ] Register a new account; duplicate-email registration is rejected
- [ ] Log in with correct/incorrect credentials
- [ ] Upload and detect objects in a sample image; verify bounding
      boxes, labels, and confidence scores render correctly
- [ ] Download annotated image, CSV, and JSON from a detection
- [ ] Confirm the detection appears in History; search/delete it
- [ ] Confirm Dashboard and Analytics reflect the new detection
- [ ] Update profile name and password
- [ ] Export a CSV/Excel/PDF report from Settings
- [ ] Promote an account to admin; confirm admin menu appears
- [ ] As admin: deactivate/reactivate a user, reset a password, delete
      an image, view system logs, create and restore a database backup

## Results

The completed system supports the full end-to-end flow: registration
through detection through reporting through administration, with no
placeholder pages remaining. Object detection produces bounding boxes,
class labels, and confidence scores for arbitrary uploaded images
using a pretrained YOLOv11 model, with configurable model size and
confidence threshold.

## Conclusion

The project demonstrates that a modern deep-learning object detection
model can be wrapped in a usable, secure, multi-user web application
using a Python-only stack, without requiring a separate JavaScript
frontend or web framework. The layered architecture keeps the codebase
maintainable and extensible for future work.

## Limitations

- SQLite and local-disk file storage do not scale to many concurrent
  writers or multiple server instances (see `docs/DEPLOYMENT.md`).
- No email-based password recovery; admin-assisted resets only.
- No automated lockout after repeated failed login attempts.
- Object detection is limited to the classes the chosen YOLOv11 model
  was trained on (COCO's 80 classes, for the stock weights).
- No built-in scheduler for automatic backups (must be triggered
  externally, e.g. via cron).

## Future Work

- Migrate to Postgres + object storage for true multi-instance
  deployment.
- Add email-based password recovery and account verification.
- Support custom/fine-tuned model uploads through the AI Management
  page.
- Add batch (multi-image) upload and detection.
- Add login rate limiting / temporary lockout after repeated failures.
- Add real-time detection via webcam or video stream.
