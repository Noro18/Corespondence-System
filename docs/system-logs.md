# System Logs — Audit Trail Implementation Plan

## Overview

Use **django-simple-history** to automatically track every create/update/delete on all models. Each tracked model gets a `_history` table recording who made the change, what changed (old value → new value), and when.

Viewable per-object in Django Admin under a "History" button.

---

## Implementation Steps

### Step 1 — Install

```bash
source corespondence-venv/bin/activate
pip install django-simple-history
pip freeze > requirements.txt
```

### Step 2 — Add to `config/settings.py`

```python
INSTALLED_APPS = [
    ...
    "simple_history",
    "apps.outbound_letters",
]
```

### Step 3 — Add `HistoricalRecords()` to Models

**`apps/inbound_letters/models.py`**

```python
from simple_history.models import HistoricalRecords

class Sender(models.Model):
    ...
    history = HistoricalRecords()

class InboundLetter(models.Model):
    ...
    history = HistoricalRecords()

class Assignment(models.Model):
    ...
    history = HistoricalRecords()
```

**`apps/outbound_letters/models.py`**

```python
from simple_history.models import HistoricalRecords

class OutboundLetter(models.Model):
    ...
    history = HistoricalRecords()

class ApprovalStage(models.Model):
    ...
    history = HistoricalRecords()
```

**`apps/accounts/models.py`**

```python
from simple_history.models import HistoricalRecords

class CustomUser(AbstractUser):
    ...
    history = HistoricalRecords()
```

### Step 4 — Update Admin to Show History

Replace `ModelAdmin` with `SimpleHistoryAdmin` in all admin.py files.

**`apps/inbound_letters/admin.py`**

```python
from simple_history.admin import SimpleHistoryAdmin

@admin.register(InboundLetter)
class InboundLetterAdmin(SimpleHistoryAdmin):
    ...

@admin.register(Assignment)
class AssignmentAdmin(SimpleHistoryAdmin):
    ...

@admin.register(Sender)
class SenderAdmin(SimpleHistoryAdmin):
    ...
```

**`apps/outbound_letters/admin.py`**

```python
from simple_history.admin import SimpleHistoryAdmin

@admin.register(OutboundLetter)
class OutboundLetterAdmin(SimpleHistoryAdmin):
    ...

@admin.register(ApprovalStage)
class ApprovalStageAdmin(SimpleHistoryAdmin):
    ...
```

**`apps/accounts/admin.py`**

```python
from simple_history.admin import SimpleHistoryAdmin

@admin.register(CustomUser)
class CustomUserAdmin(SimpleHistoryAdmin):
    ...
```

### Step 5 — Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6 — Verify

1. Log into Django Admin as ADMIN
2. Open any InboundLetter record
3. Click the **"History"** button (top-right)
4. See the audit trail

---

## Models Covered

| App | Model | Why track |
|---|---|---|
| accounts | CustomUser | Track user creation, role changes, deactivation |
| inbound_letters | Sender | Track sender info edits |
| inbound_letters | InboundLetter | Track status changes, field edits |
| inbound_letters | Assignment | Track assignment creation, status updates, completion |
| outbound_letters | OutboundLetter | Track full workflow (draft → approved → dispatched) |
| outbound_letters | ApprovalStage | (Already an audit table — optional but consistent) |

---

## What You'll See

In Django Admin, clicking "History" shows:

| Date/time | User | Change |
|---|---|---|
| 28 Jul 2026 14:30 | admin | Changed status from DRAFT to APPROVED. Changed subject |
| 28 Jul 2026 10:00 | sekretariadu | Created letter |
| 27 Jul 2026 09:15 | admin | Changed role from STAFF to SEKRETARIADU |

---

## Requirements

| Package | Purpose |
|---|---|
| `django-simple-history` | Automatic audit trail for all models |
| Zero config, works offline | No broker, no cloud, no extra services |
