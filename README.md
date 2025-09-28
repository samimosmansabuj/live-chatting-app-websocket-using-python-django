# Live Chatting App (WebSocket • Python • Django)

[![CI](https://github.com/samimosmansabuj/live-chatting-app-websocket-using-python-django/actions/workflows/django.yml/badge.svg)](https://github.com/samimosmansabuj/live-chatting-app-websocket-using-python-django/actions/workflows/django.yml)

Real-time chat application powered by **Django**, **Channels (ASGI)**, and **WebSockets**, featuring file sharing (image/video/audio/any file), voice notes (MediaRecorder), custom offers, and per-message deletion. Frontend uses **Bootstrap 5** with a polished UI and reusable `base.html`.

> Tip: Open two browsers, log into two different accounts, and chat in real-time.

---

## ✨ Features

- 🔐 Authentication (login, register, logout)
- 💬 Real-time messaging (Django Channels + WebSocket)
- 📎 Attachments: images, videos, audio, files
- 🎙️ Voice recording (MediaRecorder → upload)
- 💼 Custom offers (send/accept/decline/cancel)
- 🗑️ Per-message delete (broadcast to all clients)
- 🧭 Modern UI with `base.html` + pages:
  - Home (welcome/hero)
  - Registration / Login
  - Users list (searchable)
  - Chat room

---

## 🧱 Tech Stack

- **Backend:** Python, Django, Django Channels (ASGI), Daphne
- **Frontend:** HTML, Bootstrap 5, Vanilla JS
- **Transport:** WebSocket
- **Storage:** SQLite by default (swap to your DB if you want)

---

## 🚀 Quick Start

### 1) Clone
```bash
git clone https://github.com/samimosmansabuj/live-chatting-app-websocket-using-python-django.git
cd live-chatting-app-websocket-using-python-django
```

### 2) Create & activate venv
```bash
python -m venv env
```

#### Windows
```bash
env\Scripts\activate
```

#### macOS/Linux
```bash
source env/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure environment
##### Create `.env` from `.env.example` and adjust values:
```bash
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5) Migrate & (optionally) create superuser
##### migrate database:
```bash
python manage.py migrate
```

##### (optionally) create superuser:
```bash
python manage.py createsuperuser
```

### 5) Run (ASGI via Daphne)
##### Localhost quick start:
```bash
daphne live_chat.asgi:application
```

##### Or bind to IP/port:
```bash
daphne -b 0.0.0.0 -p 8000 live_chat.asgi:application
```

---

## 🧪 Test Real-Time Chat Locally

- Start server (Daphne).
- Open two different browsers (or normal + incognito).
- Register/login as two different users.
- Go to Users → open a chat → send messages, files, voice notes.

---

## 🧪 Test Real-Time Chat Locally
```
live-chatting-app-websocket-using-python-django/
├─ live_chat/                # Django project (settings, asgi.py)
├─ app/                      # Main app(s): models, views, urls, consumers
├─ templates/                # base.html, home, login, register, users, chat
├─ static/                   # CSS/JS (recommended to extract long inline code)
├─ manage.py
├─ requirements.txt
├─ requirements-dev.txt      # (new) dev tools
├─ tasks.py                  # (new) Invoke tasks
├─ Makefile                  # (new) developer shortcuts
├─ .github/workflows/django.yml  # (new) CI
├─ .flake8                   # (new) flake8 config
├─ pyproject.toml            # (new) Black config
└─ README.md
```

---

## ⚙️ Notes

- Use ASGI (Daphne) for WebSockets (don’t rely on classic WSGI).
- For LAN testing, add your machine’s IP to ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS.
- For production:
- Go to Users → open a chat → send messages, files, voice notes.
  - DEBUG=False, strong SECRET_KEY
  - Serve behind Nginx/HTTPS
  - Consider channels-redis for scaling

---
