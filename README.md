# DISFRULEG — Commercial Management System

A production-grade desktop application for managing a small/medium produce-distribution business: receipt generation, multi-tier pricing, client and inventory management, debt tracking, sales analytics, and an AI assistant (UbicuoAI) for natural-language operations.

Built in Python with a CustomTkinter desktop UI, MySQL / Google Cloud SQL as the data store, and a strict **Clean / Onion Architecture** across every business module.

> 🇪🇸 [Versión en español más abajo](#disfruleg--sistema-de-gestión-comercial-español)

---

## Highlights

- **11 business modules**, each implemented as a self-contained vertical slice (`domain → data → business → ui`).
- **Clean Architecture**: inner layers never depend on outer layers; dependencies are injected through `Protocol`-based interfaces.
- **Authentication & authorization** with `bcrypt` hashing, role-based access (admin / supervisor / user), 30-minute session timeout, and failed-login lockout.
- **Device authorization** layer — only registered devices can connect to production data.
- **PDF + Excel report generation** (ReportLab, FPDF, openpyxl) for receipts, sales dashboards, client rankings and product contribution.
- **UbicuoAI assistant** — natural-language queries over the operational database with unit validation across 18 measurement units and fuzzy matching.
- Runs both against **local MySQL** and **Google Cloud SQL** (via the official `cloud-sql-python-connector`).

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| Language     | Python 3.10+ |
| Desktop UI   | CustomTkinter, Tkinter |
| Database     | MySQL 8 / Google Cloud SQL |
| DB drivers   | `mysql-connector-python`, `PyMySQL`, `cloud-sql-python-connector` |
| Security     | `bcrypt`, `cryptography` |
| Reporting    | ReportLab, FPDF, PyMuPDF, openpyxl, matplotlib |
| Data / NLP   | pandas, numpy, rapidfuzz, python-Levenshtein |
| Validation   | pydantic |
| Packaging    | PyInstaller |

## Architecture

The project follows **Clean / Onion Architecture**. Each business module under `src/modules/<module>/` mirrors the same four layers:

```
ui/          ← Tkinter views & controllers (presentation)
business/    ← Use cases / services (business rules)
data/        ← Repositories (DB access only)
domain/      ← Entities, value objects, protocols
```

**Dependency rule:** UI → Business → Data → Domain. Inner layers know nothing about the outer ones; everything is wired through dependency injection using `typing.Protocol` interfaces so any layer can be swapped or unit-tested in isolation.

### Module map

| Module        | Responsibility |
|---------------|----------------|
| `auth`        | Login, sessions, password hashing |
| `security`    | Device authorization, audit |
| `modules/receipts`   | Receipt creation, folio sequencing, PDF export |
| `modules/pricing`    | Multi-tier price editor (per client group) |
| `modules/clients`    | Client and client-type management |
| `modules/inventory`  | Product catalog and stock |
| `modules/analytics`  | Sales / profit dashboards, PDF reports |
| `modules/deudas`     | Debt tracking and payments |
| `modules/importacion`| Bulk import of quotations from spreadsheets |
| `modules/users`      | System-user administration |
| `modules/ubicuoai`   | Natural-language assistant over the DB |

## Repository layout

```
.
├── main.py                  # Application entry point
├── launch_module.py         # Standalone module launcher
├── requirements.txt
├── .env.example             # Template for environment variables
├── src/
│   ├── auth/                # Authentication
│   ├── security/            # Device authorization
│   ├── database/            # Connections & cloud config
│   ├── services/            # Cross-cutting services
│   ├── ui/                  # Shared UI components
│   ├── utils/               # Helpers
│   └── modules/             # Business modules (one folder per slice)
├── data/
│   ├── sql/                 # Schema, triggers, views, sample data
│   └── fonts/               # Custom fonts for PDFs
├── docs/                    # Documentation site (mkdocs)
├── scripts/
│   ├── setup_local_db.py    # One-command database bootstrap
│   └── db_admin/            # Database admin utilities
└── assets/                  # Icons and images
```

## Getting started

### 1. Prerequisites

- Python **3.10+**
- MySQL **8.x** (local) or a Google Cloud SQL instance
- macOS, Linux, or Windows

### 2. Install

```bash
git clone https://github.com/<your-user>/disfruleg-management-system.git
cd disfruleg-management-system

python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# then edit .env with your DB credentials
```

Set `DB_MODE=local` to run against a local MySQL server, or `DB_MODE=cloud` to
use a Google Cloud SQL instance. For Cloud SQL, drop a service-account JSON
(`credentials.json`, git-ignored) in the project root, or authenticate with
`gcloud auth application-default login`.

### 4. Initialise the database

One command creates the database, applies the full schema (tables, views,
triggers), loads sample data, creates an admin user, and authorises the current
machine:

```bash
python scripts/setup_local_db.py --reset
```

It prompts for the MySQL password and for the app admin password — nothing is
hardcoded. Useful flags:

| Flag | Effect |
|------|--------|
| `--reset` | Drop and recreate the database from scratch |
| `--admin-user <name>` | Admin username to create (default: `admin`) |
| `--skip-device` | Skip auto-authorising this machine, to exercise the real device-approval flow |

### 5. Run

```bash
python main.py
```

Log in with the admin user created in step 4.

## Screenshots

Place PNG screenshots under `docs/screenshots/` and reference them here, for example:

```markdown
![Login](docs/screenshots/login.png)
![Dashboard](docs/screenshots/dashboard.png)
![Receipt builder](docs/screenshots/receipt-builder.png)
![Pricing editor](docs/screenshots/pricing-editor.png)
![UbicuoAI](docs/screenshots/ubicuoai.png)
```

## Security notes

- No secrets are stored in this repository. `.env`, `credentials.json`, and `*.key` are all git-ignored.
- All user passwords are hashed with **bcrypt** (12 rounds).
- Failed-login attempts are tracked per user; accounts auto-lock after a configurable threshold.
- All database access goes through a thin connection layer; device-authorisation gating prevents unregistered machines from connecting to production data.

## Roadmap / things I'd add next

- Replace bespoke DB access with SQLAlchemy 2.x + Alembic migrations.
- Add `pytest` coverage on the `business/` layer (the domain is already pure).
- Extract a small REST API (FastAPI) so a future web/mobile client can reuse the same business code.
- CI: GitHub Actions running ruff + mypy + pytest on every push.

## License

[MIT](./LICENSE) © 2026 Jared Aceves

---

## DISFRULEG — Sistema de Gestión Comercial (Español)

Aplicación de escritorio en Python para administrar un negocio de distribución de productos: generación de recibos, edición de precios por tipo de cliente, control de inventario, gestión de clientes, seguimiento de deudas, análisis de ventas y un asistente con IA (UbicuoAI) que entiende lenguaje natural sobre la base de datos.

Construido con **CustomTkinter** para la interfaz y **MySQL / Google Cloud SQL** para los datos, aplicando estrictamente **Arquitectura Limpia (Clean / Onion)** en cada módulo.

### Características principales

- **11 módulos de negocio**, cada uno como vertical slice independiente (`domain → data → business → ui`).
- **Arquitectura Limpia**: las capas internas nunca dependen de las externas. Las dependencias se inyectan vía interfaces (`Protocol`).
- **Autenticación y autorización** con `bcrypt`, control de roles (admin / supervisor / usuario), expiración de sesión a 30 minutos y bloqueo por intentos fallidos.
- **Autorización por dispositivo** — solo equipos registrados pueden acceder a datos productivos.
- **Reportes PDF y Excel** (ReportLab, FPDF, openpyxl) para recibos, dashboards de ventas y rankings de clientes/productos.
- **Asistente UbicuoAI** — consultas en lenguaje natural con validación de unidades (18 unidades) y fuzzy matching.
- Soporta **MySQL local** y **Google Cloud SQL**.

### Cómo correr el proyecto

```bash
git clone https://github.com/<tu-usuario>/disfruleg-management-system.git
cd disfruleg-management-system

python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env         # editar con tus credenciales (DB_MODE=local)

# Crea la base, aplica el esquema completo (tablas, vistas, triggers),
# carga datos de ejemplo, crea el usuario admin y autoriza este equipo.
# Pide las contraseñas de forma interactiva.
python scripts/setup_local_db.py --reset

python main.py
```

Para conectar a Google Cloud SQL en lugar de MySQL local, usa `DB_MODE=cloud`
en el `.env` y coloca un `credentials.json` (service account) en la raíz del
proyecto.

### Estructura del proyecto

Cada módulo bajo `src/modules/<modulo>/` respeta la misma división de capas:

```
ui/          ← vistas y controladores Tkinter (presentación)
business/    ← casos de uso / servicios (reglas de negocio)
data/        ← repositorios (solo acceso a datos)
domain/      ← entidades, value objects, protocolos
```

### Notas de seguridad

- No hay secretos en este repositorio. `.env`, `credentials.json` y `*.key` están ignorados por git.
- Contraseñas hasheadas con **bcrypt** (12 rondas).
- Conteo de intentos fallidos y bloqueo automático de cuentas.
- Capa de autorización por dispositivo para producción.

### Licencia

[MIT](./LICENSE) © 2026 Jared Aceves
