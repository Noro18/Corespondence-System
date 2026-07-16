# Architecture Document — Correspondence System

## 1. Architectural Patterns

### 1.1 MVT (Model-View-Template)

Django's native pattern. Models define data, Views handle logic, Templates render UI.

### 1.2 Service Layer Pattern

Encapsulate business logic in service modules, keeping views thin and testable.

```
View → Service → Model
```

### 1.3 Repository Pattern (via Model Managers)

Extend Django's `Manager` for reusable query logic (e.g., pending letters, overdue tasks).

### 1.4 Signal-Based Event-Driven Architecture

Use Django Signals for decoupled notification triggers (e.g., `post_save` → send notification).

### 1.5 Middleware for Global Concerns

Custom middleware for request logging, role-based menu injection, and session checks.

### 1.6 Mixin-Based Access Control

Reusable `RoleRequiredMixin`, `LoginRequiredMixin` for CBVs to enforce RBAC.

---

## 2. Recommended Libraries

| Library | Purpose | Justification |
|---|---|---|
| **django-crispy-forms** + **crispy-tailwind** | Form rendering | DRY form templates, Tailwind alignment (RNF-04) |
| **django-guardian** | Object-level permissions | Staff may have access to specific letters only |
| **django-filter** | Search/filter on letter lists | Staff needs to filter by date, status, sender |
| **django-notifications-hq** | In-app notifications | RF-10 notification system with read/unread |
| **celery** + **redis** | Async task queue | Deadline reminders, email alerts (non-blocking) |
| **django-celery-beat** | Scheduled tasks | Auto-check overdue tasks daily |
| **weasyprint** | PDF generation | RF-05 draft → generate official letter PDF |
| **django-cleanup** | Auto-delete old PDF files | Prevents orphaned file storage when records are deleted |
| **whitenoise** | Static file serving | Production static file handling integrated with Django |
| **django-debug-toolbar** | Development profiling | Performance optimization (RNF-03 < 3s) |
| **django-allauth** | Social auth (optional) | Extendable if SSO is needed later |
| **django-storages** + **S3/MinIO** | External file storage | Scale media/PDF storage beyond local disk |
| **ruff** / **black** | Code quality | Linting and formatting consistency |

### Libraries to AVOID

| Library | Reason |
|---|---|
| **django-rest-framework** | Not needed — no API requirements in SRD |
| **django-reversion** | Adds complexity; audit trail can be simpler |
| **django-taggit** | No tagging requirement in SRD |
| **django-import-export** | Not in scope |

---

## 3. Expanded Project Structure

```
paperless_office/
│
├── manage.py
├── requirements.txt
├── docker-compose.yml                 # For local dev (MySQL + Redis)
├── Dockerfile
├── Makefile                           # Common dev commands
│
├── config/                            # Project settings (root)
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py                    # Shared settings (all envs)
│   │   ├── dev.py                     # Development overrides
│   │   ├── prod.py                    # Production overrides
│   │   └── test.py                    # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   │
│   ├── accounts/                      # Authentication & RBAC
│   │   ├── models.py                  # CustomUser, Role
│   │   ├── managers.py                # UserManager (by role)
│   │   ├── services.py                # AuthService, ProfileService
│   │   ├── admin.py
│   │   ├── views.py                   # LoginView, ProfileUpdateView
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/accounts/
│   │       ├── login.html
│   │       └── profile_form.html
│   │
│   ├── common/                        # Shared utilities
│   │   ├── mixins.py                  # RoleRequiredMixin, AuditLogMixin
│   │   ├── permissions.py             # Custom permission checks
│   │   ├── decorators.py              # @role_required decorator
│   │   ├── media_protect.py           # Secure PDF serving view
│   │   ├── utils.py                   # generate_ref_code(), helpers
│   │   └── choices.py                 # Shared enums (Status, Role)
│   │
│   ├── inbound_letters/               # Karta Tama
│   │   ├── models.py                  # InboundLetter, Sender, Attachment
│   │   ├── managers.py                # InboundLetterManager
│   │   ├── services.py                # LetterRegistrationService
│   │   ├── admin.py
│   │   ├── views.py                   # ListView, CreateView, DespaxuView
│   │   ├── forms.py                   # LetterForm (PDF upload, 10MB limit)
│   │   ├── filters.py                 # InboundLetterFilter
│   │   ├── urls.py
│   │   └── templates/inbound/
│   │       ├── letter_list.html
│   │       ├── letter_detail.html
│   │       ├── letter_form.html
│   │       └── despaxu_form.html
│   │
│   ├── outbound_letters/              # Karta Sai & Approval
│   │   ├── models.py                  # OutboundDraft, ApprovalStage, Comment
│   │   ├── managers.py                # OutboundManager
│   │   ├── services.py                # DraftService, ApprovalService
│   │   ├── admin.py
│   │   ├── views.py                   # DraftView, ReviewView, ApprovalView
│   │   ├── forms.py
│   │   ├── filters.py
│   │   ├── urls.py
│   │   └── templates/outbound/
│   │       ├── draft_list.html
│   │       ├── draft_form.html
│   │       ├── draft_detail.html
│   │       ├── review_supervisor.html
│   │       └── approval_prezidente.html
│   │
│   ├── monitoring/                    # Dashboard & Follow-up
│   │   ├── models.py                  # TaskAssignment, Notification, Deadline
│   │   ├── services.py                # DashboardService, NotificationService
│   │   ├── signals.py                 # post_save → notification hooks
│   │   ├── tasks.py                   # Celery: deadline_reminder, overdue_check
│   │   ├── admin.py
│   │   ├── views.py                   # DashboardView, ReportView
│   │   ├── urls.py
│   │   └── templates/monitoring/
│   │       ├── dashboard.html
│   │       ├── follow_up_list.html
│   │       └── overdue_report.html
│   │
│   └── core/                          # (aliased to avoid name clash)
│       └── __init__.py
│
├── static/
│   ├── css/
│   │   ├── tailwind.css
│   │   └── custom.css
│   ├── js/
│   │   ├── main.js
│   │   └── dashboard-charts.js
│   └── img/
│       └── logo.png
│
├── media/
│   ├── inbound_pdfs/                  # RNF-02: no direct external access
│   └── outbound_pdfs/
│
├── templates/
│   ├── base.html                      # Layout: sidebar + topbar + content
│   ├── includes/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── notifications_dropdown.html
│   │   └── pagination.html
│   └── errors/
│       ├── 403.html
│       └── 404.html
│
├── tests/
│   ├── test_accounts.py
│   ├── test_inbound.py
│   ├── test_outbound.py
│   └── test_monitoring.py
│
└── .env.example                       # Environment variable template
```

---

## 4. Database Schema (Key Models)

### 4.1 accounts

```
CustomUser (extends AbstractUser)
├── role: CharField (ADMIN, SEKRETARIADU, PREZIDENTE, STAFF)
├── phone: CharField
├── avatar: ImageField
└── department: CharField
```

### 4.2 inbound_letters

```
Sender
├── name: CharField
├── institution: CharField
└── contact: CharField

InboundLetter
├── tracking_code: CharField (unique, auto-generated, e.g. IN-2025-0001)
├── title: CharField
├── original_ref_no: CharField (sender's reference)
├── sender: ForeignKey(Sender)
├── letter_date: DateField
├── received_date: DateTimeField (auto)
├── pdf_file: FileField (validators=[MaxSizeValidator(10MB)])
├── description: TextField
├── registered_by: ForeignKey(User → SEKRETARIADU)
├── status: CharField (REGISTERED, ASSIGNED, COMPLETED, ARCHIVED)
├── current_assignee: ForeignKey(User, nullable)
├── deadline: DateField (nullable, set by President)
└── notes: TextField (President's despatch notes)

Assignment
├── letter: ForeignKey(InboundLetter)
├── assigned_by: ForeignKey(User → PREZIDENTE)
├── assigned_to: ForeignKey(User → STAFF)
├── instructions: TextField
├── due_date: DateField (RF-08)
├── status: CharField (PENDING, IN_PROGRESS, COMPLETED)
├── completion_report: TextField
└── completed_at: DateTimeField (nullable)
```

### 4.3 outbound_letters

```
OutboundDraft
├── tracking_code: CharField (unique, auto, e.g. OUT-2025-0001)
├── title: CharField
├── recipient: CharField
├── recipient_address: TextField
├── body_content: TextField
├── generated_pdf: FileField (nullable — WeasyPrint output)
├── created_by: ForeignKey(User)
├── created_at: DateTimeField
├── status: CharField (DRAFT, IN_REVIEW, APPROVED, REJECTED, SENT)
└── final_ref_no: CharField (nullable, set on approval)

ApprovalStage
├── draft: ForeignKey(OutboundDraft)
├── stage_order: IntegerField (1 = Supervisor, 2 = President)
├── reviewer: ForeignKey(User)
├── status: CharField (PENDING, APPROVED, REJECTED)
├── comment: TextField
└── decided_at: DateTimeField (nullable)
```

### 4.4 monitoring

```
Notification
├── recipient: ForeignKey(User)
├── title: CharField
├── message: TextField
├── is_read: BooleanField (default=False)
├── notification_type: CharField (NEW_TASK, DEADLINE_SOON, OVERDUE, APPROVAL)
├── related_url: CharField (nullable — deep link)
└── created_at: DateTimeField
```

---

## 5. Approval Workflow Design

```
[Staff/Sekretariadu]
    │  Create OutboundDraft (status=DRAFT)
    ▼
[Supervisor/Diretor]
    │  Review → Approve or Reject
    │  If Approve: stage moves to President
    ▼
[Prezidente]
    │  Final Approval → Approve (status=APPROVED, assign final_ref_no)
    │              or Reject (status=REJECTED, send back with notes)
    ▼
[Final]
    │  Approved → PDF generated, letter marked as SENT
    │  Rejected → Draft returned to creator for revision
```

**State Machine (simplified):**

```
DRAFT → IN_REVIEW → APPROVED → SENT
                       ↓
                   REJECTED → DRAFT (revision loop)
```

---

## 6. RBAC Implementation Strategy

### 6.1 Role-Based Menu Injection

Use a middleware or template context processor to inject role-appropriate menu items:

| Role | Visible Menu Items |
|---|---|
| ADMIN | Users (CRUD), Logs, All Letters, Settings |
| SEKRETARIADU | Register Letter, All Inbound, Draft Outbound |
| PREZIDENTE | Dashboard, Despaxu, Approval, Reports |
| STAFF | My Tasks, My Drafts |

### 6.2 View-Level Access Control

```python
# mixins.py
class RoleRequiredMixin(AccessMixin):
    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

# Usage
class DespaxuView(RoleRequiredMixin, UpdateView):
    allowed_roles = [Role.PREZIDENTE]
    ...
```

### 6.3 Role Enum

```python
class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador / TI'
    SEKRETARIADU = 'SEK', 'Sekretariadu'
    PREZIDENTE = 'PREZ', 'Prezidente / Autoridade'
    STAFF = 'STF', 'Staff / Funsionariu'
```

---

## 7. Notification System

### 7.1 Trigger Points (Signals)

| Event | Signal | Notification Target |
|---|---|---|
| New letter registered | `post_save` on InboundLetter | President |
| Assignment created | `post_save` on Assignment | Assigned Staff |
| Approval decision made | `post_save` on ApprovalStage | Draft creator |
| Deadline approaching (3 days) | Celery beat — daily check | Task assignees |
| Deadline overdue | Celery beat — daily check | Task assignees + President |

### 7.2 Celery Tasks

```python
# tasks.py
@shared_task
def check_deadline_reminders():
    """Runs daily — sends notifications for upcoming/overdue deadlines."""
    ...

@shared_task
def send_weekly_summary():
    """Optional: weekly email to President with pending items."""
    ...
```

---

## 8. Security Architecture

| Concern | Implementation |
|---|---|
| Password hashing | Django default (PBKDF2 + SHA256) per RNF-01 |
| Media file protection | Custom view wrapper — `X-Accel-Redirect` (nginx) or Django `FileResponse` with login check per RNF-02 |
| Session security | `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True` in prod |
| CSRF | Django CSRF middleware (included by default) |
| XSS | Django template auto-escaping |
| SQL injection | Django ORM (parameterized queries) |
| Rate limiting | `django-ratelimit` on login endpoint |
| Audit logging | `django-auditlog` or custom `LogEntry` model for sensitive actions |

---

## 9. Performance & Caching

- **Template caching** for dashboard stats (cache key per user, invalidate on change)
- **Database indexing** on `status`, `tracking_code`, `assigned_to`, `due_date`
- **Database query optimization** — use `select_related()` and `prefetch_related()` in views
- **Pagination** on all list views (25 items per page default)
- **Redis** for Celery broker + cache backend

---

## 10. Environment Configuration (`.env`)

```
DJANGO_SETTINGS_MODULE=config.settings.dev
SECRET_KEY=
DEBUG=True

DB_NAME=paperless_office
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

REDIS_URL=redis://localhost:6379/0

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 11. Development Setup Order

1. Set up virtual environment + install dependencies
2. Configure `config/settings/` with 3-tier settings (base/dev/prod)
3. `accounts` app — CustomUser model, authentication views, RBAC mixins
4. `common` app — Shared mixins, choices, utilities
5. `inbound_letters` app — Models, services, views, filters
6. `outbound_letters` app — Draft, approval workflow
7. `monitoring` app — Dashboard, notifications, Celery tasks
8. Templates — Base layout, partials, responsive UI with Tailwind
9. Tests — 80%+ coverage across all apps
10. Docker + CI/CD pipeline
