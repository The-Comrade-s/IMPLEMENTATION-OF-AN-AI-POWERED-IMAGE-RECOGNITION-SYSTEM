# MASTER PROMPT -- Gateway ICT Polytechnic Saapade Alumni Portal Management System

You are an expert Software Architect, UI/UX Designer, Senior Full-Stack
Engineer, Database Engineer, DevOps Engineer and Security Engineer.

Your task is to build a COMPLETE production-ready web application named:

**Gateway ICT Polytechnic Saapade Alumni Portal Management System**

## Branding

-   Use the uploaded official Gateway ICT Polytechnic logo throughout
    the application (navbar, login, footer, favicon, loading screen).
-   Use the previously approved modern alumni portal interface as the
    design inspiration.
-   Do not copy it exactly; improve it into a premium university portal.

## Objective

Build a responsive, scalable, secure alumni management system that could
realistically be deployed by Gateway ICT Polytechnic.

## Tech Stack

Frontend: - React + Next.js + TypeScript - TailwindCSS - shadcn/ui -
Framer Motion - Chart.js

Backend: - Laravel 12 REST API - Sanctum Authentication

Database: - PostgreSQL

Deployment: - GitHub - Render - Automatic deployment from GitHub -
Environment variables - Production-ready configuration

## Design

Primary #0B2D6B Accent Gold #D4AF37 White cards Rounded 12px Poppins
font Professional SaaS dashboard Responsive (Desktop/Tablet/Mobile) Dark
and Light mode

## Roles

Guest Alumni Class Representative Administrator Super Administrator

## System Hierarchy

Gateway ICT Polytechnic → Schools → Departments → Programme (ND/HND) →
Graduation Year → Alumni

Admin must create Schools, Departments, Programmes and Graduation Years
dynamically (no hardcoding).

## Core Modules

-   Landing page
-   Authentication
-   Dashboard
-   Alumni Directory
-   Profile Management
-   Jobs
-   Events
-   News
-   Messaging
-   Notifications
-   Reports
-   Admin Panel
-   Settings

## Landing Page

Hero, statistics, latest news, events, CTA, footer, logo.

## Authentication

Register, Login, Forgot Password, Email Verification, Remember Me.

Registration fields: Full Name Email Phone Matric Number School
Department Programme Graduation Year Password

## Dashboard

Cards: Total Alumni Jobs Events Messages Notifications Recent Activity
Charts

## Alumni Directory

Search/filter by: School Department Programme Graduation Year Occupation
Location Employment Status Skills

## Profile

Photo Bio Academic History Employment Skills Social Links Achievements

## Jobs

CRUD Company Position Salary Deadline Location Apply Link

## Events

CRUD Registration Attendance Gallery Countdown

## News

CRUD Categories Pinned announcements

## Messaging

Inbox Conversation Notifications

## Admin

Dashboard Manage Users Manage Schools Manage Departments Manage
Programmes Manage Graduation Years Approve Alumni Manage Representatives
Manage Jobs Manage Events Manage News Reports Settings

## Reports

PDF CSV Excel Charts

## Database Tables

users roles schools departments programmes graduation_years
alumni_profiles representatives jobs events event_registrations messages
notifications news audit_logs settings

Use foreign keys, indexes and timestamps.

## Security

RBAC CSRF XSS prevention SQL Injection prevention Validation Password
hashing Audit logging Rate limiting

## UI Requirements

Sidebar Top navbar Breadcrumbs Professional tables Pagination Search
Export Loading skeletons Toast notifications Responsive navigation Empty
states

## Folder Structure

Separate frontend and backend. Reusable components. Service layer.
Repository pattern where appropriate. RESTful APIs.

## Deployment

Source: GitHub Hosting: Render Database: Render PostgreSQL CI/CD: Auto
deploy on push Production environment variables

## Deliverables

Generate: - Complete frontend - Complete backend - Database migrations -
Seeders - Controllers - Models - Policies - Middleware - Validation -
APIs - Authentication - Professional UI - Documentation - README -
Installation guide - Production-ready code

Ensure the final application looks and behaves like a real university
alumni management platform suitable for Gateway ICT Polytechnic Saapade.
