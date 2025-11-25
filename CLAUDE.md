# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Buzzer App** - A Progressive Web App for iPhone that enables users to remotely ring devices within groups. Users create accounts, form groups, and trigger individual devices to ring with customizable durations (30s, 1min, 2min, or continuous).

**Critical Constraint**: For a device to be ringable, the PWA must remain open on that device (can be on lock screen, but cannot be swiped away). This is an iOS limitation requiring the app to maintain an active WebSocket connection.

## Architecture Overview

### Backend (FastAPI + PostgreSQL)

**Purpose**: Handles authentication, device management, group coordination, and real-time ring command routing via WebSockets.

**Key Components**:
- **FastAPI Application** (`backend/app/main.py`): Entry point with REST API endpoints and WebSocket handler
- **WebSocket Manager** (`backend/app/websocket/manager.py`): Maintains active device connections, routes ring commands, broadcasts device status
- **Database Models** (`backend/app/models/`): SQLAlchemy ORM models for users, groups, devices, ring sessions
- **Services** (`backend/app/services/`): Business logic for authentication, ring coordination, device tracking
- **API Endpoints** (`backend/app/api/`): RESTful endpoints for auth, groups, devices, ring control

**WebSocket Flow**:
1. Client connects with JWT token: `ws://host/ws/{device_id}?token={jwt}`
2. ConnectionManager stores device_id -> WebSocket mapping
3. 30s heartbeat keeps connection alive, tracks device online/offline status
4. Ring commands routed via WebSocket to target device
5. Device sends confirmation (ring_started) and stop status back

### Frontend (Vanilla JavaScript PWA)

**Purpose**: Provides UI for user authentication, group management, device viewing, and ring control. Installable on iOS Home Screen.

**Key Components**:
- **Authentication** (`static/js/auth.js`): Login/register flow, JWT token storage
- **WebSocket Client** (`static/js/websocket.js`): Maintains connection, handles reconnection with exponential backoff, routes incoming messages
- **Audio Manager** (`static/js/audio.js`): **CRITICAL COMPONENT** - Handles iOS audio unlock mechanism (requires user interaction before playback), loops ringtone, manages duration timers
- **Device Manager** (`static/js/device.js`): Generates device UUID, collects device info, registers with backend
- **Dashboard UI** (`dashboard.html`): Main interface showing groups, devices, online status, ring controls
- **PWA Configuration** (`manifest.json`, `service-worker.js`): Installation manifest, asset caching, offline fallback

**Audio Implementation (iOS-Critical)**:
- HTML5 `<audio>` element with loop enabled (not Web Audio API - doesn't work in iOS background)
- Requires user interaction (touch/click) to unlock before audio can play
- Wake Lock API prevents screen sleep during ringing
- Manual stop button on device that initiated ring

### Database Schema

```
users: id, email, password_hash, full_name, created_at
groups: id, name, owner_id, invite_code, created_at
group_members: id, group_id, user_id, role, joined_at
devices: id, user_id, device_name, device_id (UUID), device_type, browser_info, last_seen, is_online
ring_sessions: id, group_id, initiated_by, target_device_id, duration_seconds, status, started_at, stopped_at
```

**Key Design Decisions**:
- Device tracking via client-generated UUID stored in browser localStorage
- Online status via 60s heartbeat timeout
- Ring sessions track full lifecycle (initiated → ringing → stopped/completed)
- Groups use invite codes for joining

## Development Commands

### Backend Setup
```bash
# Create Python virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize PostgreSQL database
# Configure DATABASE_URL in .env first
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# No build step needed - serve static files
# Frontend is served by FastAPI at / when running backend

# For frontend-only testing, use any simple HTTP server:
cd frontend
python -m http.server 8000
```

### Testing
```bash
# Backend tests (when implemented)
pytest backend/tests -v

# Single test file
pytest backend/tests/test_auth.py -v

# With coverage
pytest --cov=app backend/tests
```

### Database Migrations
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Code Quality
```bash
# Lint backend code
flake8 backend/app

# Format code
black backend/app

# Type checking
mypy backend/app
```

## Project Structure

### Backend
```
backend/
├── app/
│   ├── main.py                 # FastAPI app, WebSocket endpoint
│   ├── config.py              # Environment configuration
│   ├── database.py            # SQLAlchemy setup, session management
│   ├── models/                # Database models
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── device.py
│   │   └── ring_session.py
│   ├── schemas/               # Pydantic request/response models
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── device.py
│   │   └── ring.py
│   ├── api/                   # API endpoints organized by resource
│   │   ├── deps.py            # Dependency injection (auth, db)
│   │   ├── auth.py            # Auth endpoints
│   │   ├── groups.py          # Group endpoints
│   │   ├── devices.py         # Device endpoints
│   │   └── rings.py           # Ring control endpoints
│   ├── websocket/
│   │   ├── manager.py         # Connection manager & routing
│   │   └── handlers.py        # WebSocket message handlers
│   ├── services/              # Business logic
│   │   ├── auth_service.py    # JWT, password hashing
│   │   ├── device_service.py  # Device status tracking
│   │   └── ring_service.py    # Ring coordination
│   └── utils/
│       └── security.py        # Cryptographic utilities
├── alembic/                   # Database migrations
├── requirements.txt
├── .env                       # Environment variables (DO NOT COMMIT)
└── Dockerfile
```

### Frontend
```
frontend/
├── index.html                 # Login/registration page
├── dashboard.html             # Main app interface
├── manifest.json              # PWA manifest
├── service-worker.js          # Caching & offline support
├── offline.html               # Offline fallback page
└── static/
    ├── css/
    │   ├── main.css          # Login page styles
    │   └── dashboard.css     # Dashboard styles
    ├── js/
    │   ├── app.js            # Main app initialization
    │   ├── auth.js           # Login/register flow
    │   ├── websocket.js      # WebSocket client
    │   ├── audio.js          # Audio manager
    │   ├── device.js         # Device registration
    │   └── ui.js             # UI helpers
    ├── audio/
    │   └── ringtone.mp3
    └── icons/
        ├── icon-72x72.png
        ├── icon-96x96.png
        ├── icon-192x192.png   # iPhone HomeScreen icon
        ├── icon-512x512.png   # Splash screen
        └── ... (other sizes)
```

## Implementation Phases

### Phase 1: Backend Foundation (Must Complete First)
Create FastAPI app structure, database models, and authentication endpoints. Everything depends on this.

**Files to create**:
- `backend/app/main.py` - FastAPI app entry point
- `backend/app/database.py` - PostgreSQL connection
- `backend/app/models/*` - SQLAlchemy models
- `backend/app/utils/security.py` - JWT, password hashing
- `backend/app/api/auth.py` - Register/login endpoints
- `alembic/versions/*` - Initial schema migration

**Verification**: Can register/login and receive JWT token via POST requests

### Phase 2: WebSocket Infrastructure
Build real-time communication layer for device connectivity and ring commands.

**Files to create**:
- `backend/app/websocket/manager.py` - Connection tracking
- `backend/app/main.py` - Add WebSocket endpoint `/ws/{device_id}`
- `backend/app/api/devices.py` - Device registration endpoint
- `backend/app/services/device_service.py` - Online/offline tracking

**Verification**: Device can connect via WebSocket, receives heartbeat echo

### Phase 3: Frontend Core
Build authentication and basic UI structure.

**Files to create**:
- `frontend/index.html` - Login/register form
- `frontend/dashboard.html` - Main UI shell
- `frontend/static/js/auth.js` - JWT token management
- `frontend/static/js/websocket.js` - WebSocket client
- `frontend/static/css/main.css` - Styling

**Verification**: Can login/register, see device list, connect WebSocket

### Phase 4: Audio & Ring Control
Implement iOS audio handling and ring command flow (Phase 5 follows after this).

**Files to create**:
- `frontend/static/js/audio.js` - **CRITICAL** iOS audio unlock
- `backend/app/services/ring_service.py` - Ring logic
- `backend/app/api/rings.py` - Ring endpoints
- `frontend/static/js/app.js` - Ring button handlers

**Testing**: Manually test audio on iOS device - this is critical and often breaks

### Phase 5: PWA Configuration
Make app installable on iOS.

**Files to create**:
- `frontend/manifest.json` - PWA metadata
- `frontend/service-worker.js` - Asset caching
- Add meta tags to HTML files (apple-mobile-web-app-capable, etc)
- Generate icons (72, 96, 128, 144, 152, 192, 384, 512px)

**Verification**: iOS Safari shows "Add to Home Screen" option, works in standalone mode

### Phase 6: Polish & Deployment
Error handling, UI improvements, testing, and production deployment.

## Common Development Tasks

### Adding a New Ring Duration Option
1. Update `ring_sessions` table schema if needed
2. Modify `POST /api/rings/start` schema validation
3. Update ring service to handle new duration
4. Update dashboard UI with new duration button
5. Test on actual iOS device

### Debugging WebSocket Issues
1. Check browser DevTools Network tab (filter for WS)
2. Inspect WebSocket frames in browser console
3. Verify JWT token in query parameter
4. Check backend logs for connection/message errors
5. Ensure device UUID is stored in localStorage

### Testing Ring Audio on iOS
1. Install PWA on actual iPhone (not simulator)
2. Open app, ensure "Connected" status shows
3. Use another device to ring it
4. Check: audio plays, volume is max, can hear from lock screen
5. Click stop button - audio should stop immediately

### Checking Device Online Status
- Devices marked offline after 60s without heartbeat
- Backend has periodic task to mark inactive devices
- Frontend should show status indicator (green = online, gray = offline)
- Disable ring button for offline devices

## Important Notes

### iOS PWA Limitations
- **Audio**: Use HTML5 `<audio>` element, NOT Web Audio API
- **Background**: App must stay open; use 30s heartbeat to keep connection
- **Permissions**: No native APIs; all audio via HTML5
- **SSL**: Absolutely required for PWA - won't work on HTTP

### Security
- JWT tokens stored in localStorage (secure but subject to XSS)
- All WebSocket messages must include device_id for routing
- Rate limit ring commands to prevent spam
- Validate group membership before allowing ring command

### Performance
- WebSocket connection reused for all real-time communication
- Don't recreate WebSocket on every message
- Cache group/device list in localStorage where appropriate
- Lazy load device lists if groups get large

## Deployment Troubleshooting

### Common Deployment Errors & Fixes

#### Python Version Issue
**Error**: `error: metadata-generation-failed` when installing dependencies

**Root Cause**: Render defaults to Python 3.13, but some packages don't have pre-built wheels for 3.13

**Fix**: Create `.python-version` file in project root with content:
```
3.11
```

#### Alembic Configuration Error
**Error**: `FAILED: No 'script_location' key found in configuration`

**Root Cause**: `alembic.ini` missing the `script_location` key

**Fix**: Ensure `backend/alembic.ini` contains:
```ini
[alembic]
sqlalchemy.url = driver://user:pass@localhost/dbname
script_location = alembic
```

#### SQLAlchemy TypeError
**Error**: `TypeError: Additional arguments should be named <dialectname>_<argument>, got 'indexes'`

**Root Cause**: Invalid `__table_args__` syntax in SQLAlchemy models

**Fix**: Use proper SQLAlchemy syntax for constraints:
```python
from sqlalchemy import UniqueConstraint

class GroupMember(Base):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='uq_group_user_membership'),
    )
```

#### Build Succeeded but App Won't Start
**Symptoms**: Build completes but app exits with error

**Debug Steps**:
1. Check Render logs for Python error traceback
2. Verify all imports in `app/main.py` resolve correctly
3. Ensure environment variables are set (DATABASE_URL, SECRET_KEY)
4. Test locally: `uvicorn app.main:app` from backend directory
5. Check for syntax errors in models and schemas

#### Database Migration Errors
**Error**: `sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable)`

**Cause**: Migration trying to create table that already exists

**Fix**:
1. SSH into Render service (if available)
2. Check: `psql -d $DATABASE_URL -c "\dt"` to see existing tables
3. May need to manually drop problematic tables if migrations are out of sync
4. Re-run: `alembic upgrade head`

### Deployment Process on Render.com

1. **Prerequisites**:
   - GitHub repository created with all code committed
   - PostgreSQL database created on Render
   - Environment variables configured

2. **Initial Setup**:
   - Click "Create New" → "Web Service"
   - Connect GitHub repo (buzzer-app)
   - Configure build command: `pip install -r backend/requirements.txt && cd backend && alembic upgrade head`
   - Configure start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     - `DATABASE_URL`: PostgreSQL connection string (from Render PostgreSQL service)
     - `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
     - `DEBUG`: `False`

3. **Monitor Deployment**:
   - Go to Web Service dashboard
   - Click "Logs" tab to watch build progress
   - Look for "Build succeeded" message
   - Service URL appears at top once live

4. **Post-Deployment**:
   - Visit service URL in browser
   - Verify login page loads
   - Test registration and login flow
   - Install on iPhone and test ringing feature

### When to Re-deploy
- After any code commits to GitHub (Render auto-deploys)
- Manual redeploy: Service dashboard → "Manual Deploy" button
- Useful for testing environment variable changes without code commit

## Deployment

**Recommended**: Render.com (free tier available, auto SSL, PostgreSQL included)

**Production Setup**:
1. Set DATABASE_URL environment variable (PostgreSQL)
2. Set SECRET_KEY for JWT signing
3. Enable HTTPS (required for PWA)
4. Frontend files served as static assets by FastAPI
5. WebSocket endpoint at wss://domain.com/ws/{device_id}

**Pre-deployment Checklist**:
- [ ] SSL certificate configured (REQUIRED)
- [ ] Database backups configured
- [ ] Environment variables set (not in code)
- [ ] Tested on actual iOS device with production domain
- [ ] Ring audio plays on lock screen
- [ ] WebSocket reconnection works

## References

- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [iOS PWA Limitations - firt.dev](https://firt.dev/notes/pwa-ios/)
- [Web Audio API vs HTML5 Audio](https://stackoverflow.com/questions/60003027/ios-pwa-background-audio-support)
- [PWA Web App Manifest](https://web.dev/learn/pwa/web-app-manifest)
