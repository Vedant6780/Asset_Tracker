# 📦 Real-Time Asset Tracking & Workflow API — Project Documentation

> A complete guide to how this project was built from scratch — covering every technology choice, architectural decision, and line of code.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack & Why Each Was Chosen](#2-technology-stack--why-each-was-chosen)
3. [Project Structure](#3-project-structure)
4. [Backend Deep Dive](#4-backend-deep-dive)
5. [Frontend Deep Dive](#5-frontend-deep-dive)
6. [Real-Time Architecture](#6-real-time-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Database Design](#8-database-design)
9. [How to Run the Project](#9-how-to-run-the-project)
10. [API Reference](#10-api-reference)

---

## 1. Project Overview

### The Problem
In enterprise supply chains, asset tracking is often done via manual spreadsheet entry. This leads to:
- **Data lag** — managers don't see updates until operators manually file reports
- **Human error** — typos, duplicate entries, missing records
- **No audit trail** — impossible to trace who moved what and when

### The Solution
A **real-time backend API** coupled with a **modern React frontend** that:
- Lets **warehouse operators** scan/input asset IDs and update statuses instantly
- Gives **logistics managers** a live, auto-updating dashboard with complete audit trails
- Enforces **role-based access control** so operators can only update statuses, while managers have full CRUD access
- Maintains an **immutable audit log** of every single status change

---

## 2. Technology Stack & Why Each Was Chosen

### Backend

| Technology | Version | Why We Chose It |
|-----------|---------|-----------------|
| **Django** | 5.1.2 | Robust, battle-tested Python web framework. Provides built-in ORM, admin capabilities, user management, and security primitives. |
| **Django REST Framework** | 3.15.2 | The industry standard for building Web APIs in Django. Provides ViewSets, serializers, status codes, and declarative URL routing. |
| **SimpleJWT** | 5.3.1 | JSON Web Token authentication plugin for DRF. Provides secure token generation, validation, and role-based payload claims. |
| **Django Channels & Daphne** | 4.1.x | Async WebSocket capabilities integrated with Django's event loop for real-time dashboard updates. |
| **SQLite** | 3.x | Zero-config relational database engine. Easily replaceable with PostgreSQL/MySQL in production. |

### Frontend

| Technology | Version | Why We Chose It |
|-----------|---------|-----------------|
| **React** | 19.x | Component-based architecture for building complex UIs. Virtual DOM for efficient re-renders — critical when real-time events update the dashboard. |
| **Vite** | 7.x | Next-generation build tool. Sub-second hot module replacement (HMR) during development. Much faster than Create React App or Webpack. |
| **React Router** | 7.x | Client-side routing for SPA navigation. Handles protected routes (redirecting unauthenticated users) and role-based route access. |
| **Vanilla CSS** | — | Full design control. We built a custom design system with CSS custom properties (variables), glassmorphism effects, gradient animations, and micro-interactions. No dependency on utility frameworks. |

---

## 3. Project Structure

```
workflow API/
├── backend/                       # Django REST Framework backend
│   ├── api/                       # Core application app
│   │   ├── models.py              # CustomUser, Asset, AuditLog ORM models
│   │   ├── views.py               # AssetViewSet, CustomTokenObtainPairView
│   │   ├── serializers.py         # DRF Serializers with audit trail support
│   │   ├── urls.py                # App URL routing
│   │   └── management/commands/   # Custom management commands (seed_db)
│   ├── core/                      # Project configuration (settings, urls, asgi, wsgi)
│   ├── manage.py                  # Django CLI runner
│   └── requirements.txt           # Python dependencies
├── frontend/                      # React (Vite) frontend
│   ├── src/
│   │   ├── main.jsx               # React DOM entry point
│   │   ├── App.jsx                # Router & AuthProvider setup
│   │   ├── index.css              # Glassmorphic CSS design system
│   │   ├── api.js                 # Centralized fetch wrapper & WS factory
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Global Authentication context
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx      # Glassmorphic login
│   │   │   ├── OperatorDashboard.jsx  # Operator scanner interface
│   │   │   └── ManagerDashboard.jsx   # Live operational dashboard
│   │   └── components/
│   │       ├── AssetTable.jsx     # Asset listing table
│   │       ├── AuditPanel.jsx     # Side audit panel
│   │       └── StatusBadge.jsx    # Status indicators
│   ├── package.json
│   └── vite.config.js
└── PROJECT_DOCUMENTATION.md       # Full documentation
```

---

## 4. Backend Deep Dive

### 4.1 Application Entry Point (`main.py`)

The FastAPI app uses the **lifespan** pattern (replacing the deprecated `@app.on_event`):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()           # Create tables if they don't exist
    async with async_session() as session:
        await seed_data(session)  # Insert demo data on first run
    yield                     # App runs here
```

**CORS middleware** is configured to allow the React dev server (`localhost:5173`) to make cross-origin requests. In production, you'd restrict this to your actual domain.

### 4.2 Database Layer (`database.py`)

We use SQLAlchemy's modern async pattern:

```python
engine = create_async_engine("sqlite+aiosqlite:///./asset_tracking.db")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

The `get_db()` dependency provides a session per request with automatic commit/rollback:

```python
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 4.3 ORM Models (`models.py`)

Three models form the core data layer:

**User** — Stores credentials and role:
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="operator")  # "admin" or "operator"
```

**Asset** — The trackable entity:
```python
class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    serial_number = Column(String(50), unique=True)
    status = Column(String(50), default="Registered")
    location = Column(String(100), default="Unknown")
```

**AuditLog** — Immutable history (append-only):
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    asset_id = Column(Integer, ForeignKey("assets.id"))
    action = Column(String(50))       # "CREATED", "STATUS_UPDATE"
    old_status = Column(String(50))
    new_status = Column(String(50))
    changed_by = Column(String(50))   # Who made this change
    changed_at = Column(DateTime)     # When
```

### 4.4 Pydantic Schemas (`schemas.py`)

FastAPI uses Pydantic models for **automatic request validation**. If a client sends invalid data, they get a 422 error with details — no manual validation needed:

```python
class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    serial_number: str = Field(..., min_length=1, max_length=50)
    location: str = Field("Warehouse A", max_length=100)
```

### 4.5 Authentication (`auth.py`)

Passwords are hashed with bcrypt before storage:
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

JWTs contain the username and role as claims:
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=60)
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

The `get_current_user` dependency extracts the user from any request's `Authorization: Bearer <token>` header. The `require_role("admin")` dependency adds role enforcement on top.

### 4.6 Asset Router (`asset_router.py`)

The status update endpoint is the heart of the system:

```python
@router.put("/{asset_id}/status")
async def update_asset_status(asset_id, payload, db, current_user):
    # 1. Find asset
    # 2. Save old status
    # 3. Update to new status
    # 4. Create AuditLog entry
    # 5. Broadcast via WebSocket ← This is the real-time magic
    await ws_manager.broadcast({
        "event": "status_update",
        "asset_id": asset.id,
        "new_status": payload.new_status,
        "updated_by": current_user.username,
    })
```

### 4.7 WebSocket Manager (`websocket_manager.py`)

Simple but effective — maintains a list of active connections and broadcasts to all:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
```

---

## 5. Frontend Deep Dive

### 5.1 Design System (`index.css`)

We built a custom dark-mode design system with:
- **CSS Custom Properties** — 40+ design tokens for colors, spacing, shadows, and transitions
- **Glassmorphism** — `backdrop-filter: blur(20px)` with semi-transparent backgrounds
- **Animated Gradients** — Radial gradients that shift with a 20-second CSS animation
- **Micro-animations** — Status badge pulse, row flash on update, slide-in panels, scale-in success overlays
- **Responsive Grid** — `grid-template-columns: repeat(auto-fit, minmax(180px, 1fr))` for dynamic stat cards

### 5.2 Auth Context (`AuthContext.jsx`)

React Context provides global auth state:

```jsx
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [role, setRole] = useState(() => localStorage.getItem('role'));
  // login() → POST /api/v1/auth/login → store JWT → redirect
  // logout() → clear localStorage → redirect to login
}
```

### 5.3 Protected Routes (`App.jsx`)

```jsx
function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, role } = useAuth();
  if (!isAuthenticated) return <Navigate to="/" />;
  if (requiredRole && role !== requiredRole) return <Navigate to={...} />;
  return children;
}
```

### 5.4 Operator Dashboard

The operator flow:
1. **Scan/type** a serial number into a large, high-contrast input
2. `GET /api/v1/assets/lookup/{serial_number}` fetches the asset
3. A card displays the asset info with a **status dropdown**
4. On submit, `PUT /api/v1/assets/{id}/status` updates the status
5. A **full-screen green flash overlay** confirms success
6. The input clears and auto-focuses for the next scan

### 5.5 Manager Dashboard

The manager dashboard has four key sections:
1. **Stat Cards** — Total assets, In Transit, Delivered, Needs Attention (animated counters)
2. **Asset Data Table** — Sortable, clickable rows with status badges
3. **Live Connection Indicator** — Green pulsing dot when WebSocket is connected
4. **Audit Side Panel** — Slides in from the right, showing a timeline of every status change with timestamps and user attribution

### 5.6 Real-Time Updates

When the WebSocket receives a `status_update` event:
```jsx
setAssets((prev) =>
  prev.map((a) =>
    a.id === data.asset_id
      ? { ...a, status: data.new_status, location: data.location }
      : a
  )
);
setFlashId(data.asset_id);  // Triggers yellow flash animation on the row
```

---

## 6. Real-Time Architecture

```
┌──────────────┐                    ┌──────────────────┐
│   Operator    │─── PUT /status ──▶│                  │
│   (React)     │                   │   FastAPI         │
└──────────────┘                    │   Backend         │
                                    │                  │
┌──────────────┐◀── WebSocket ─────│  ws_manager      │
│   Manager     │   broadcast       │  .broadcast()    │
│   (React)     │                   │                  │
└──────────────┘                    └────────┬─────────┘
                                             │
                                    ┌────────▼─────────┐
                                    │   SQLite DB       │
                                    │   (Asset +        │
                                    │    AuditLog)      │
                                    └──────────────────┘
```

1. Operator calls `PUT /api/v1/assets/{id}/status`
2. Backend updates the database and creates an AuditLog entry
3. Backend calls `ws_manager.broadcast()` with the event payload
4. All connected manager dashboards receive the JSON via WebSocket
5. React state updates → the affected row flashes yellow → status badge changes

---

## 7. Security Architecture

| Layer | Mechanism |
|-------|-----------|
| **Password Storage** | bcrypt hash (never plaintext) |
| **Authentication** | JWT Bearer tokens in Authorization header |
| **Authorization (RBAC)** | `require_role("admin")` dependency on protected endpoints |
| **WebSocket Auth** | JWT validated from query parameter before accepting connection |
| **SQL Injection** | Prevented by SQLAlchemy ORM (parameterized queries) |
| **Input Validation** | Pydantic models reject malformed payloads with 422 errors |
| **CORS** | Restricted to known dev server origins |
| **Audit Trail** | Every change logged with user + timestamp (immutable) |

---

## 8. Database Design

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│   users      │       │   assets      │       │  audit_logs   │
├─────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)       │──┐    │ id (PK)       │
│ username     │       │ name          │  │    │ asset_id (FK) │◀─┘
│ hashed_pass  │       │ serial_number │  └───▶│ action        │
│ role         │       │ status        │       │ old_status    │
│ created_at   │       │ location      │       │ new_status    │
└─────────────┘       │ created_at    │       │ changed_by    │
                       │ updated_at    │       │ changed_at    │
                       └──────────────┘       └──────────────┘
```

---

## 9. How to Run the Project

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server (auto-creates DB and seeds demo data)
python -m uvicorn main:app --reload --port 8000
```

The backend will be live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive Swagger documentation.

### Frontend

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

The React app will be live at `http://localhost:5173`.

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Manager (Admin) | `admin` | `admin123` |
| Operator | `operator` | `operator123` |

---

## 10. API Reference

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| `POST` | `/api/v1/auth/login` | None | Any | Login and get JWT |
| `GET` | `/api/v1/assets` | JWT | Admin | List all assets |
| `GET` | `/api/v1/assets/{id}` | JWT | Admin | Get asset + audit history |
| `GET` | `/api/v1/assets/lookup/{serial}` | JWT | Any | Find asset by serial number |
| `POST` | `/api/v1/assets` | JWT | Admin | Create new asset |
| `PUT` | `/api/v1/assets/{id}/status` | JWT | Any | Update status (triggers WS broadcast) |
| `DELETE` | `/api/v1/assets/{id}` | JWT | Admin | Delete asset |
| `WS` | `/api/v1/ws/dashboard?token=...` | JWT (query) | Admin | Live dashboard WebSocket |
