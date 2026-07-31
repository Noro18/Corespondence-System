# PROGRESS.md — Project Progress

## ✅ Implemented

### Foundation
- [x] Project configured: AUTH_USER_MODEL, LOGIN_*, INSTALLED_APPS, TEMPLATES DIRS, MEDIA/STATIC
- [x] Removed Celery/Redis/RabbitMQ; replaced with Django management commands + system cron
- [x] AGENTS.md created with project guide and important rules
- [x] RBAC plan documented (docs/rbac-plan.md)

### Authentication & Accounts
- [x] CustomUser model with RBAC roles (ADMIN/SEK/PREZ/STF) and CustomUserManager
- [x] Custom login page with Tailwind styling (templates/accounts/login.html)
- [x] Custom logout — GET-based, logs out and redirects to /login/
- [x] CustomUserAdmin with role field on create and edit forms

### User Management (ADMIN-only CRUD)
- [x] UserListView — paginated table (25 per page) with status badges and action buttons
- [x] UserCreateView — form with all fields: username, name, email, role, phone, department, password
- [x] UserUpdateView — edit form including is_active toggle
- [x] UserDeleteView — deactivates (is_active=False) instead of hard-delete
- [x] CustomUserCreationForm / CustomUserChangeForm — override Django's built-in forms for CustomUser
- [x] Sidebar "Users" link (ADMIN only); topbar "Admin" link guarded (ADMIN only)

### Inbound Letters
- [x] Sender, InboundLetter, Assignment models with migrations
- [x] Auto-generated tracking code (LTR-YYYYMMDD-NNNN) via save() override
- [x] InboundLetterAdmin and AssignmentAdmin registered

### Outbound Letters
- [x] OutboundLetter model with status workflow (Draft → In Review → Approved/Rejected → Dispatched)
- [x] ApprovalStage model for full audit trail (who, when, decision, comments)
- [x] Auto-generated tracking code (OUT-YYYYMMDD-NNNN)
- [x] OutboundLetterListView — role-scoped (ADMIN/PREZ see all, others see own)
- [x] OutboundLetterCreateView — PDF upload + metadata form with date picker widget
- [x] OutboundLetterDetailView — letter info + approval history timeline
- [x] OutboundLetterReviewView — PREZ/ADMIN can approve or reject with comments
- [x] OutboundLetterDispatchView — ADMIN marks as dispatched
- [x] OutboundLetterDeleteView — ADMIN only
- [x] Date picker (type="date") for letter_date field
- [x] 5 templates (list, form, detail, review, delete confirm)
- [x] Sidebar links: "My Drafts" (SEK/STF/ADMIN), "Outbound Approvals" (PREZ/ADMIN)

### Dashboard & Monitoring
- [x] DashboardView with role-scoped data (ADMIN/PREZ/SEK = all, STF = own)
- [x] Stats cards (pending, in progress, overdue)
- [x] Recent Inbound Letters table
- [x] My Tasks table
- [x] Overdue assignments alert
- [x] Role-based sidebar menu

### Access Control
- [x] RoleRequiredMixin (base class for role-based view guarding)
- [x] AdminMixin, SekretariaduMixin, PrezidenteMixin, StaffMixin
- [x] Anonymous user guard (is_authenticated check before .role access)

### Other
- [x] Password validators removed (any password accepted)
- [x] Logout link fixed (admin:logout → accounts:logout)
- [x] UI labels changed from Tetum to English
- [x] django-cleanup integrated (auto-deletes PDF files on record deletion)

---

## 📝 Remaining (per RBAC plan)

### Inbound Letters — Custom Views
- [ ] Custom list/detail/create views (currently using Django Admin links)
- [ ] Assignment review/dispatch UI for PREZ (issue #12)
- [ ] Inline PDF preview + first-page thumbnail (issue #13)

### Outbound Letters — Missing
- [ ] PDF generation from template (not needed if using Word → PDF upload)
- [ ] Edit view for drafts (currently only create, no update)

### Missing Features
- [ ] **Reports** — ADMIN/PREZ overdue reports, letter statistics
- [ ] **Notifications** — in-app notification system for all roles
- [ ] **Senders link** should be restricted to SEK/ADMIN only (currently visible to all)
- [ ] **My Tasks** for STF should be a custom filtered view (currently links to admin changelist)
- [ ] **Inbound letter detail view** — needs custom template with approval history

### Known Issues
- [ ] #6 — UI: Active label and checkbox misaligned in user edit form

---

## 🗺️ Sidebar by Role (current state)

### ADMIN
- Dashboard, Users, Register Letter, All Inbound Letters, Assignments, Senders, My Drafts, Outbound Approvals

### SEKRETARIADU
- Dashboard, Register Letter, All Inbound Letters, Assignments, Senders, My Drafts

### PREZIDENTE
- Dashboard, All Inbound Letters, Assignments, Senders, Outbound Approvals

### STAFF
- Dashboard, My Tasks, Senders, My Drafts
