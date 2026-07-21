# RBAC Plan — Role-Based Access Control

## 1. Role Definitions

| Role | Codigu | Deskrisaun |
|---|---|---|
| ADMIN | `ADMIN` | Administrador / TI — full system control |
| SEKRETARIADU | `SEK` | Sekretariadu — rejistu karta, draft karta sai |
| PREZIDENTE | `PREZ` | Prezidente / Autoridade / Diretór — despaxu, aprovasaun, monitorizasaun |
| STAFF | `STF` | Staff / Funsionariu — asuntu karta, relatóriu konkluzaun |

---

## 2. Permission Matrix

| Feature | ADMIN | SEKRETARIADU | PREZIDENTE | STAFF |
|---|---|---|---|---|
| **User Management** | | | | |
| List/Create/Edit/Delete users | CRUD | — | — | — |
| **Inbound Letters** | | | | |
| Register new letter | ✓ | ✓ | — | — |
| View all letters | ✓ | ✓ | ✓ | assigned only |
| Edit letter details | ✓ | own only | notes field only | — |
| Delete letter | ✓ | — | — | — |
| Upload PDF | ✓ | ✓ | — | — |
| **Despatch (Assignment)** | | | | |
| Create assignment (despaxu) | ✓ | — | ✓ | — |
| View all assignments | ✓ | ✓ | ✓ | own only |
| Update progress/completion | — | — | — | ✓ |
| **Outbound Letters** | | | | |
| Create draft | ✓ | ✓ | — | ✓ |
| Review draft (1st stage) | ✓ | — | ✓ | — |
| Approve/Reject (2nd stage) | ✓ | — | ✓ | — |
| Generate final PDF | ✓ | — | ✓ | — |
| **Monitoring** | | | | |
| View dashboard | ✓ | ✓ | ✓ | ✓ |
| View all overdue tasks | ✓ | ✓ | ✓ | own only |
| **Notifications** | | | | |
| View in-app notifications | ✓ | ✓ | ✓ | ✓ |
| Mark as read/unread | ✓ | ✓ | ✓ | ✓ |

---

## 3. Implementation Layers

### 3.1 Model Level — Role Field

Already implemented in `CustomUser.role` with `TextChoices`:

```python
class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    SEKRETARIADU = "SEK", "Sekretariadu"
    PREZIDENTE = "PREZ", "Prezidente"
    STAFF = "STF", "Staff"
```

### 3.2 View Level — RoleRequiredMixin

Guard views by allowed roles:

```python
# apps/common/mixins.py
from django.contrib.auth.mixins import AccessMixin

class RoleRequiredMixin(AccessMixin):
    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class SekretariaduMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.SEKRETARIADU]

class PrezidenteMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.PREZIDENTE]

class StaffMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.STAFF]
```

Usage:
```python
class DespaxuView(PrezidenteMixin, UpdateView):
    ...
```

### 3.3 Template Level — Role-Based Menu & Visibility

In templates, conditionally show/hide elements:

```django
{% if user.role == 'ADMIN' or user.role == 'PREZ' %}
  <a href="{% url 'despaxu' %}">Despaxu</a>
{% endif %}

{% if user.role == 'SEK' %}
  <a href="{% url 'register_letter' %}">Rejistu Karta</a>
{% endif %}
```

### 3.4 Object Level — django-guardian

For fine-grained permissions (e.g., "Staff A can only see their assigned letters"):

```python
from guardian.shortcuts import assign_perm, get_objects_for_user

# Assign permission when creating assignment
assign_perm('view_letter', staff_user, letter)

# Filter queryset
letters = get_objects_for_user(request.user, 'view_letter')
```

---

## 4. Menu Structure by Role

```
ADMIN:
├── Dashboard
├── Users (CRUD)
├── Karta Tama → All Letters, Register
├── Karta Sai → All Drafts, Approvals
├── Asuntu Karta → All Assignments
└── Reports

SEKRETARIADU:
├── Dashboard
├── Karta Tama → Register, All Letters
├── Karta Sai → Create Draft, My Drafts
└── Remetente → Manage Senders

PREZIDENTE:
├── Dashboard
├── Karta Tama → All Letters (for despatch)
├── Karta Sai → Approvals Pending
├── Asuntu Karta → All Assignments
└── Overdue Reports

STAFF:
├── Dashboard
├── Ha'u-nia Tarefa → My Assignments
├── Karta Sai → My Drafts
└── Notifications
```

---

## 5. Implementation Steps

### Phase 1 — Foundation (done)
- [x] Add `role` field to `CustomUser` model
- [x] Define `Role` enum with `TextChoices`

### Phase 2 — Common Mixins (next sprint)
- [ ] Create `apps/common/mixins.py` with `RoleRequiredMixin`
- [ ] Add `SekretariaduMixin`, `PrezidenteMixin`, `StaffMixin`
- [ ] Create `@role_required` decorator for function views

### Phase 3 — View Guarding (as views are built)
- [ ] Apply mixins to all CBVs
- [ ] Return 403 for unauthorized access
- [ ] Redirect to login for unauthenticated

### Phase 4 — Template Guards
- [ ] Add role checks in `base.html` sidebar
- [ ] Add role checks in list/detail templates
- [ ] Hide action buttons users can't use

### Phase 5 — Object-Level (optional)
- [ ] Integrate `django-guardian`
- [ ] Assign permissions on letter creation
- [ ] Filter querysets by user permissions

---

## 6. Audit & Accountability

Every sensitive action must be logged:

| Action | Logged By |
|---|---|
| User login/logout | Django auth logs |
| Letter registered | `registered_by` FK on InboundLetter |
| Assignment created | `assigned_by` FK on Assignment |
| Draft approved/rejected | `ApprovalStage.reviewer` FK |
| Letter deleted | `django-auditlog` or simple history |

---

## 7. References

- [Architecture Document — RBAC Section](../docs/architecture.md#6-rbac-implementation-strategy)
- [Django Guardian Docs](https://django-guardian.readthedocs.io/)
