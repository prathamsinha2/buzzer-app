# Buzzer - Web Push Device Finder

A Progressive Web App (PWA) that enables users to remotely "buzz" devices in their group using Web Push Notifications. Works on iOS, Android, and Desktop.

## Features

- ✅ **Cross-Platform PWA:** Installable on iOS (Add to Home Screen), Android, and Desktop.
- ✅ **Web Push Notifications:** Uses standard Web Push API (VAPID) to deliver notifications even when the app is closed (on supported platforms).
- ✅ **Real-Time Status:** See which devices are Online/Offline via WebSockets.
- ✅ **Group Management:** Create groups, join via invite codes, and manage members.
- ✅ **"Find My Device":** Buzz your own devices from the dashboard.
- ✅ **Offline Support:** Service Worker caches assets for offline access.

## Tech Stack

- **Backend:** FastAPI (Python), SQLAlchemy, PyWebPush, SQLite (Dev) / PostgreSQL (Prod).
- **Frontend:** Vanilla JavaScript, HTML5, CSS3.
- **Real-time:** WebSockets for status updates.
- **Notifications:** Web Push API + Service Workers.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js (optional, for dev tools)

### Local Development

1.  **Clone the repo:**
    ```bash
    git clone <your-repo-url>
    cd buzzer_app
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Database Migration:**
    ```bash
    # This will create the local SQLite database
    alembic upgrade head
    ```

4.  **Generate VAPID Keys:**
    The app uses VAPID keys for push notifications. You can generate them using:
    ```bash
    # Inside backend/ directory
    python -c "from pywebpush import WebPusher; print(WebPusher(private_key='').generate_vapid_keys())"
    ```
    Save the output to `backend/vapid.json`:
    ```json
    {
        "private_key": "YOUR_PRIVATE_KEY",
        "public_key": "YOUR_PUBLIC_KEY",
        "email": "mailto:admin@example.com"
    }
    ```

5.  **Run Server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

6.  **Access App:**
    Open `http://localhost:8000` in your browser.

## Deployment (Render.com)

1.  **Create Web Service:**
    - Connect your GitHub repository.
    - **Runtime:** Python 3.
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2.  **Environment Variables:**
    Add these in the Render Dashboard:
    - `DATABASE_URL`: Your PostgreSQL URL (or use SQLite for testing).
    - `SECRET_KEY`: A random string for security.
    - `VAPID_PRIVATE_KEY`: Content of your private key (full string).
    - `VAPID_PUBLIC_KEY`: Content of your public key.
    - `VAPID_CLAIMS_EMAIL`: `mailto:your@email.com`.

3.  **Database:**
    - The app includes an auto-migration script in `main.py` that runs on startup to ensure the database schema is correct.

## Usage Guide

### iOS (iPhone/iPad)
**Important:** Web Push on iOS requires the app to be installed on the Home Screen.
1.  Open the website in **Safari**.
2.  Tap the **Share** button (box with arrow).
3.  Scroll down and tap **"Add to Home Screen"**.
4.  Open the "Buzzer" app from your home screen.
5.  Login and click "Enable Notifications".

### Android / Desktop
1.  Open the website in Chrome/Edge.
2.  Login and click "Enable Notifications" when prompted.
3.  (Optional) Click the "Install" icon in the address bar for a native app experience.

### Buzzing a Device
1.  Go to **"My Devices"** to buzz your own registered devices.
2.  Or create a **Group**, invite friends, and buzz their devices from the Group view.
3.  **Online Devices:** Will show a full-screen overlay alert.
4.  **Offline Devices:** Will receive a system notification.

## Project Structure

```
buzzer_app/
├── backend/
│   ├── app/
│   │   ├── api/           # API Endpoints
│   │   ├── models/        # DB Models
│   │   ├── services/      # Business Logic (Push/Ring)
│   │   └── main.py        # App Entry Point
│   ├── alembic/           # Migrations
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── js/            # Frontend Logic (app.js, notifications.js)
│   │   └── images/        # Icons
│   ├── service-worker.js  # Push Handler
│   ├── manifest.json      # PWA Config
│   └── dashboard.html
└── README.md
```

## License
Open Source.
