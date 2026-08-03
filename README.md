# 📦 Real-Time Asset Tracking & Workflow API

[![Django](https://img.shields.io/badge/Django-5.1.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15.2-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![JWT Auth](https://img.shields.io/badge/SimpleJWT-5.3.1-black?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

A real-time enterprise asset tracking and logistics workflow management system. Designed to replace manual spreadsheet entry with instant status updates, role-based access control (RBAC), live manager dashboards, and an immutable audit trail.

---

## 🌟 Key Features

- **⚡ Real-Time Operational Dashboard**: Live synchronization for logistics managers via WebSocket streams and rapid API polling fallback.
- **🔐 Role-Based Access Control (RBAC)**: Distinct workflows for **Operators** (rapid serial search & status update) and **Managers** (full asset lifecycle management, audit logs, and metrics).
- **📜 Immutable Audit Logging**: Every asset status and location change is automatically logged with timestamp and user attribution.
- **🎨 Glassmorphic Modern UI**: Custom CSS design system with sleek dark mode, micro-animations, status badge indicators, and dynamic state transitions.
- **🛡️ JWT Authentication**: Secured via `djangorestframework-simplejwt` token authentication with automated refresh and session state management.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.1.2 & Django REST Framework (DRF) 3.15.2
- **Authentication**: `djangorestframework-simplejwt` (JWT Token-based Auth & RBAC)
- **Database**: SQLite (ORM-managed via Django Models with prefetching optimizations)
- **CORS & Async Support**: `django-cors-headers`, `channels`, `daphne`

### Frontend
- **Framework**: React 19 + Vite 7
- **Routing**: React Router 7 (Protected & Role-Gated Routes)
- **State & API**: Custom React Context (`AuthContext`) and centralized Fetch API wrapper
- **Styling**: Vanilla CSS custom tokens (Glassmorphism, animations, responsive grid layouts)

---

## 📁 Repository Structure

```text
├── backend/                       # Django REST Framework Backend
│   ├── api/                       # Core API app (Models, Views, Serializers, URLs)
│   │   ├── models.py              # CustomUser, Asset, AuditLog ORM models
│   │   ├── views.py               # AssetViewSet, CustomTokenObtainPairView
│   │   ├── serializers.py         # DRF Serializers with nested audit logs
│   │   ├── urls.py                # Router registration & endpoints
│   │   └── management/commands/   # Custom management commands (seed_db)
│   ├── core/                      # Project configuration (settings, urls, asgi, wsgi)
│   ├── manage.py                  # Django management script
│   └── requirements.txt           # Python dependencies
├── frontend/                      # React (Vite) Single-Page Application
│   ├── src/
│   │   ├── components/            # Reusable UI components (AssetTable, AuditPanel, etc.)
│   │   ├── context/               # AuthContext state provider
│   │   ├── pages/                 # LoginPage, ManagerDashboard, OperatorDashboard
│   │   ├── api.js                 # Centralized HTTP & WebSocket API client
│   │   ├── App.jsx                # Application root with role-aware routes
│   │   └── index.css              # Design system tokens and animations
│   ├── package.json               # Node.js dependencies
│   └── vite.config.js             # Vite development server config
└── PROJECT_DOCUMENTATION.md       # Full architecture & technical implementation guide
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `3.10+`
- **Node.js**: `18.0+`
- **npm**: `9.0+`

---

### 1️⃣ Backend Setup (Django DRF)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell / CMD)
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Seed initial demo data (Users & Assets):
   ```bash
   python manage.py seed_db
   ```

6. Start the backend server:
   ```bash
   python manage.py runserver 8000
   ```
   > 💡 Backend API will be available at `http://127.0.0.1:8000`

---

### 2️⃣ Frontend Setup (React + Vite)

1. Open a new terminal tab and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Launch the development server:
   ```bash
   npm run dev
   ```
   > 💡 Frontend application will be available at `http://localhost:5173`

---

## 🔑 Demo Credentials

The database seeder (`seed_db`) initializes the system with default test accounts:

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Manager (Admin)** | `admin` | `admin123` | Full CRUD access, Real-time Dashboard, Audit Panel, Asset Creation & Deletion |
| **Operator** | `operator` | `operator123` | Asset Serial Lookup, Status Update, Scanner Workflow Interface |

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Auth Required | Role | Description |
| :--- | :--- | :---: | :---: | :--- |
| `POST` | `/api/v1/auth/login` | ❌ | Any | Authenticate user & retrieve JWT access token + user details |
| `POST` | `/api/v1/auth/refresh` | ❌ | Any | Refresh expired JWT access token |
| `GET` | `/api/v1/assets` | 🟢 JWT | Any | Fetch list of all assets with pre-fetched audit history |
| `POST` | `/api/v1/assets` | 🟢 JWT | Manager | Create a new asset entry |
| `GET` | `/api/v1/assets/lookup/{serial}` | 🟢 JWT | Any | Look up specific asset details by serial number |
| `PUT` | `/api/v1/assets/{id}/status` | 🟢 JWT | Any | Update asset status & location (Generates AuditLog) |
| `PUT` | `/api/v1/assets/{id}` | 🟢 JWT | Manager | Modify full asset properties |
| `DELETE` | `/api/v1/assets/{id}` | 🟢 JWT | Manager | Remove an asset from the system |

---

## 📄 Documentation

For an in-depth explanation of the architecture, security model, ORM database design, and real-time design decisions, refer to [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md).

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
