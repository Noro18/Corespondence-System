# DOKUMENTU SPESIFIKASAUN REKIZITU SISTEMA (SRD)

**Naran Projetu:** Sistema Jestaun Karta Tama no Sai ho Fluxu Aprovasaun no Monitorizasaun (Correspondence System)

**Institusaun Alvu:** Gabinete Prezidente Autoridade RAEOA / ZEEMS-TL

**Dezenvolvedór:** Pio & Jesti (Estajiáriu / Informatika UNTL)

---

## 1. Introdusaun

### 1.1 Objetivu

Dokumentu ne'e kria hodi define rekizitu hotu ba dezenvolvimentu sistema dijitál ba Gabinete Prezidente Autoridade RAEOA. Meta boot husi sistema ne'e mak atu troka sirkulasaun dokumentu fiziku (papél) ba formádu dijitál (paperless), nune'e bele hasae efisiente sirkulasaun, kontrola sasin desizaun (audit trail), no fó monitorizasaun (follow-up) ne'ebé lalais ba karta sira.

### 1.2 Eskopu Sistema

Sistema ne'e sei kobre sirkulasaun karta hotu iha Gabinete laran, kobre:

- Rejistu no upload karta tama formatu PDF.
- Despaxu ka distribuisaun asuntu karta (assignment) husi Prezidente ba Gabinete/Funsionáriu.
- Dezenvolvimentu razaun karta sai no fluxu aprovasaun hierárkiku.
- Kontrola prazu (deadline tracking) ba asuntu karta sira ne'ebé fó ona.

---

## 2. Deskrisaun Jerál (General Description)

### 2.1 Utilizadór Sistema (User Roles & Permissions)

Sistema ne'e uza métodu RBAC (Role-Based Access Control) ho divizaun kargu hanesan tuir mai ne'e:

| Kargu (Role) | Kbiit no Permisaun (Permissions) |
|---|---|
| **Administradór / TI** | Jestiona konta utilizadór (CRUD), reset password, kontrola seguransa no haree system logs. |
| **Sekretariadu** | Input karta tama foun, upload PDF, fó kódigu referénsia, kria rasun karta sai, no kria arkivu finál. |
| **Prezidente / Autoridade / Diretór** | Fó despaxu/asuntu karta, halo monitorizasaun ba kargo hotu, halo aprovasaun (Approve/Reject) ba karta sai, no fó komentáriu. |
| **Staff / Funsionáriu** | Simu asuntu karta (follow-up) husi Prezidente/Diretór, atualiza progresu servisu, no submete relatóriu konkluzaun. |

### 2.2 Rejime Funsaun (Use Case Diagram - Esbosu)

Utilizadór hotu sei asesu sistema bazeia ba sira-nia kbiit. Ezemplu: Funsionáriu labele asesu menu aprovasaun nian, no Sekretária labele fó despaxu ba funsionáriu seluk se la hetan autorizasaun husi Prezidente.

---

## 3. Rekizitu Funsionál (Functional Requirements)

Rekizitu funsionál sira-ne'e mak funsaun loloos ne'ebé ita sei kria ho Django Framework:

### 3.1 Módulu Autentikasaun (Authentication)

- **RF-01 (Login/Logout):** Sistema tenke kria autentikasaun seguru. Utilizadór ne'ebé la login labele asesu ba pajina laran.
- **RF-02 (User Profile):** Utilizadór ida-idak bele haree no edita sira-nia dadus pesoál (naran, email, no Perfil fotografia).

### 3.2 Módulu Karta Tama (Inbound Letters)

- **RF-03 (Rejistu Karta Tama):** Sekretariadu input dadus karta (títulu, no. referénsia orijinál, remetente, data) no upload kópia PDF (límiti 10MB).
- **RF-04 (Despaxu Prezidente):** Prezidente bele haree lista karta tama, hili kargo/funsionáriu ne'ebé responsavel, no tau nota orientasaun (follow-up instructions).

### 3.3 Módulu Karta Sai & Aprovasaun (Outbound & Approval)

- **RF-05 (Drafting):** Staff ka Sekretariadu bele dezenvolve razaun (draft) karta sai.
- **RF-06 (Workflow Approval):** Razaun (reasoning) karta sei haruka ba Supervisór/Diretór ba faze review antes haruka ba Prezidente ba aprovasaun finál.
- **RF-07 (Desizaun & Komentáriu):** Prezidente bele hili Aprova (karta hetan kódigu referénsia finál) ka Rejeita (karta tenke dezenvolve fali ho nota hadi'a nian).

### 3.4 Módulu Monitorizasaun & Dashboard (Follow-up & Analytics)

- **RF-08 (Task Deadline):** Bainhira Prezidente kria asuntu karta follow-up, tenke define due date (prazu).
- **RF-09 (Interactive Dashboard):** Dashboard Prezidente nian tenke hatudu estatistika:
  - Hira mak karta pendente (hein desizaun).
  - Hira mak asuntu karta la'o hela.
  - Hira mak asuntu karta ne'ebé atrasadu (liu ona prazu).
- **RF-10 (Notification System):** Haruka alerta automatiku iha sistema laran bainhira funsionáriu ida simu asuntu karta foun ka bainhira prazu atu besik ona.

---

## 4. Rekizitu Non-Funsionál (Non-Functional Requirements)

### 4.1 Seguransa (Security)

- **RNF-01 (Data Encryption):** Password utilizadór tenke uza hashing seguru default Django (PBKDF2 ho SHA256).
- **RNF-02 (Secure Media Access):** Ficheiru PDF karta nian labele asesu husi li'ur (públiku) se la login ba sistema (protesaun pasta media / uza Django view wrapper).

### 4.2 Dezempeñu & Disponibilidade (Performance & Usability)

- **RNF-03 (Performance):** Tempu hatán (loading page) labele liu 3 segundu.
- **RNF-04 (Mobile Responsive):** Sistema bele asesu ho di'ak uza Smartphone (bazeia ba kbiit Bootstrap/Tailwind CSS), fasil ba Prezidente atu aprova karta maski iha li'ur.

### 4.3 Arkitektura no Teknolojia

- **RNF-05 (Framework):** Django Framework 5.x.
- **RNF-06 (Database):** MySQL

---

## 5. Matriz Rastreabilidade (Traceability Matrix)

Atu hatudu ba Supervisor katak sistema ne'e efisiente duni hodi troka papél, ita uza tabela liga-ba-problema ne'e:

| Kódigu Rekizitu | Funsaun Sistema | Problema ne'ebé Solusiona (Effectiveness) |
|---|---|---|
| RF-03 | Upload PDF | **Zero Paper:** Reduz gastu ba kertas, fotokópia, no espasu armajenamentu fiziku. |
| RF-04 & RF-07 | Despaxu & Nota Dijitál | **Lalais:** Prezidente bele despaxu no aprova dokumentu maski la'o hela iha li'ur. |
| RF-08 & RF-09 | Prazu no Dashboard | **Anti-Lakon:** Evita karta monu subar, no halo monitorizasaun monitoriza-andu sai fasil liu. |

---

## 6. Tree (Project Structure)

```
paperless_office/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── config/                                          # Projetu settings prinsipál
│   ├── __init__.py
│   ├── settings.py                                  # RNF-05 Django 5.x, RNF-06 MySQL config
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   │
│   ├── accounts/                                    # 3.1 Módulu Autentikasaun
│   │   ├── models.py                                # User, Role (Admin/Sekretariadu/Prezidente/Staff)
│   │   ├── views.py                                 # RF-01 Login/Logout, RF-02 User Profile
│   │   ├── forms.py
│   │   ├── permissions.py                           # RBAC — kontrola kbiit tuir Role
│   │   ├── urls.py
│   │   └── templates/accounts/
│   │       ├── login.html
│   │       └── profile.html
│   │
│   ├── inbound_letters/                             # 3.2 Módulu Karta Tama
│   │   ├── models.py                                # Karta, ReferenciaKodigu, Remetente
│   │   ├── views.py                                 # RF-03 Rejistu, RF-04 Despaxu
│   │   ├── forms.py                                 # Upload PDF (límiti 10MB)
│   │   ├── urls.py
│   │   └── templates/inbound/
│   │       ├── lista_karta.html
│   │       └── despaxu_form.html
│   │
│   ├── outbound_letters/                            # 3.3 Módulu Karta Sai & Aprovasaun
│   │   ├── models.py                                # Draft, WorkflowApproval, Komentariu
│   │   ├── views.py                                 # RF-05 Drafting, RF-06 Workflow, RF-07 Desizaun
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/outbound/
│   │       ├── draft_form.html
│   │       ├── review_supervisor.html
│   │       └── aprovasaun_prezidente.html
│   │
│   ├── monitoring/                                  # 3.4 Módulu Monitorizasaun & Dashboard
│   │   ├── models.py                                # TaskDeadline, Notification
│   │   ├── views.py                                 # RF-08 Deadline, RF-09 Dashboard
│   │   ├── signals.py                               # RF-10 Notification automátiku
│   │   ├── urls.py
│   │   └── templates/monitoring/
│   │       ├── dashboard.html
│   │       └── atrasu_report.html
│   │
│   └── core/
│       ├── mixins.py                                # Role-based access mixins
│       ├── media_protect.py                         # RNF-02 Secure Media Access (view wrapper)
│       └── utils.py                                 # Shared utilities
│
├── static/
│   ├── css/                                         # Bootstrap/Tailwind — RNF-04 Mobile Responsive
│   ├── js/
│   └── img/
│
├── media/
│   ├── karta_tama/                                  # RNF-02 — labele asesu direta husi li'ur
│   └── karta_sai/
│
└── templates/
    ├── base.html
    └── partials/
        ├── navbar.html
        └── sidebar.html
```
