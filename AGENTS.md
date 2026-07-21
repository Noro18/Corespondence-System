# AGENTS.md — Project Guide for AI Assistants

## Project Overview

Sistema Jestaun Karta Tama no Sai ho Fluxu Aprovasaun no Monitorizasaun.
A Django-based correspondence system for RAEOA / ZEEMS-TL government office.

## Key Documents

- [RBAC Plan](docs/rbac-plan.md) — Role definitions, permission matrix, and implementation plan
- [Architecture](docs/architecture.md) — System architecture, libraries, database schema
- [SRD](docs/SRD.md) — Functional and non-functional requirements (Tetum)

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 6.0.7 |
| Frontend | Tailwind CSS (via django-tailwind) |
| DB | SQLite (dev) / MySQL (prod) |
| PDF | WeasyPrint |
| Auth | django-guardian (object-level permissions) |
| Task Scheduling | Django management commands + system cron |

## RBAC Summary

4 roles: **ADMIN** (full access), **SEKRETARIADU** (register letters, draft outgoing), **PREZIDENTE** (despatch, approve, monitor), **STAFF** (assigned tasks only).

See [RBAC Plan](docs/rbac-plan.md#2-permission-matrix) for the full permission matrix.

## Coding Conventions

- Use `RoleRequiredMixin` from `apps.common.mixins` for view-level access control
- Use `CustomUser.Role` enum for role checks in templates
- Always use `on_delete=models.PROTECT` for government-critical FKs
- Add `created_at` / `updated_at` to every model
- Write templates in English (user-facing labels, statuses, buttons)
