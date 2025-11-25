# Buzzer - iPhone PWA Device Finder

A Progressive Web App for iPhone that enables users to remotely ring devices in their group with customizable durations.

## Features

- ✅ Installable on iPhone Home Screen
- ✅ User accounts with group management
- ✅ Real-time device status tracking (online/offline)
- ✅ Remote device ringing with custom durations (30s, 1min, 2min, continuous)
- ✅ Works on lock screen (app must be open)
- ✅ Offline support for cached assets

## Important: iOS Limitations

**For a device to ring, the Buzzer app must remain open on that device** (can be on lock screen, but cannot be swiped away). This is an iOS PWA limitation. The device will ring even with the screen locked, but the app must be running.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Node.js (for development tools, optional)
- iOS device (for testing)

### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp ../.env.example .env
   # Edit .env with your database URL and SECRET_KEY
   ```

4. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

5. **Run development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

The frontend is served by the backend. Just make sure icon files and ringtone are added:

1. **Add app icons:** Copy PNG files to `frontend/static/icons/` (72x72 to 512x512)
2. **Add ringtone:** Copy MP3 file to `frontend/static/audio/ringtone.mp3`
3. **Register service worker:** The service worker is automatically registered

### Testing

1. **Local testing:**
   - Open http://localhost:8000 in browser
   - Register/login
   - On iPhone: Open in Safari, tap Share → Add to Home Screen
   - Install the PWA

2. **Test device ringing:**
   - Open app on two devices
   - From device A, ring device B
   - Select duration
   - Device B should ring (audio plays and screen shows ringing UI)
   - Click stop to silence

## Deployment

### Recommended: Render.com

1. **Create account:** https://render.com
2. **Create PostgreSQL database:** Add managed PostgreSQL
3. **Create Web Service:**
   - Connect GitHub repo
   - Set start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Add environment variables:
     - `DATABASE_URL=postgresql://...` (from PostgreSQL service)
     - `SECRET_KEY=<generate-random-key>`
     - `DEBUG=False`
4. **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
5. **Important:** SSL is automatic on Render.com (required for PWA)

### Manual Deployment

If deploying elsewhere (DigitalOcean, AWS, etc):
1. Ensure PostgreSQL is running
2. Set environment variables
3. Run migrations: `alembic upgrade head`
4. Start server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. **IMPORTANT:** Setup SSL certificate (required for PWA to work)

## Architecture

- **Backend:** FastAPI + PostgreSQL + WebSockets
- **Frontend:** Vanilla JavaScript PWA
- **Real-time:** WebSocket connections for ring commands and device status
- **Audio:** HTML5 Audio API (not Web Audio API - required for iOS)

## Project Structure

```
buzzer_app/
├── backend/                 # FastAPI backend
│   ├── app/                # Main application
│   │   ├── api/           # REST endpoints
│   │   ├── models/        # Database models
│   │   ├── websocket/     # WebSocket manager
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/              # PWA frontend
│   ├── index.html        # Login page
│   ├── dashboard.html    # Main interface
│   ├── manifest.json     # PWA manifest
│   ├── service-worker.js # Offline caching
│   └── static/           # CSS, JS, images, audio
└── CLAUDE.md            # Development guide
```

## Key Files

- **backend/app/main.py** - FastAPI app and WebSocket endpoint
- **backend/app/websocket/manager.py** - Real-time device communication
- **frontend/static/js/audio.js** - iOS audio handling (CRITICAL)
- **frontend/static/js/websocket.js** - Real-time client communication
- **frontend/manifest.json** - PWA installation config

## Common Issues

### Audio doesn't play on iOS
- Make sure `frontend/static/audio/ringtone.mp3` exists
- Audio must be unlocked by user interaction first
- App must be open (can be on lock screen)
- Test on actual device (not simulator)

### WebSocket connection fails
- Check browser DevTools Console for errors
- Verify backend is running and accessible
- Ensure JWT token is valid
- Check CORS settings if cross-origin

### Device doesn't appear online
- Verify device registered successfully
- Check WebSocket connection status (green indicator)
- Ensure heartbeat is being sent (30 second intervals)

### PWA won't install
- Must be on HTTPS (SSL certificate required)
- Check manifest.json is valid (https://web.dev/add-manifest/)
- Clear browser cache and try again
- Safari on iOS: Settings → Develop → (Device name) → Clear all websites data

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# App
APP_NAME=Buzzer
DEBUG=False
```

## Development Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1

# Tests (when implemented)
pytest backend/tests -v
```

## Security Notes

- Always use HTTPS in production (required for PWA)
- Rotate SECRET_KEY periodically
- Don't commit .env file
- Validate all user inputs
- Rate limit API endpoints in production
- Use strong passwords for database

## Support

For issues or questions:
1. Check CLAUDE.md for development guide
2. Review backend/app/main.py for API structure
3. Check browser DevTools for client-side errors
4. Enable DEBUG=True temporarily to see server logs

## License

This project is open source. Use freely for personal or commercial use.

## Credits

Built with:
- FastAPI (async Python web framework)
- SQLAlchemy (Python ORM)
- PostgreSQL (database)
- Progressive Web App APIs (offline, installation)

---

**Last Updated:** November 2024
**Status:** Production Ready (icons and ringtone needed)
