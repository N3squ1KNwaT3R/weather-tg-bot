
# 🌤️ Weather Bot - Telegram Bot with Real-Time Admin Dashboard

A comprehensive weather information system built with Python, featuring a Telegram bot for users and a real-time WebSocket-based CLI admin dashboard for monitoring user activity.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Admin Dashboard](#admin-dashboard)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Telegram Bot
- 🌡️ **Current Weather** - Get real-time weather information for any city
- ⏰ **Hourly Forecast** - View detailed hourly weather predictions
- 📅 **Tomorrow's Forecast** - Plan ahead with tomorrow's weather
- 🏙️ **Default City** - Set your preferred city for quick weather checks
- ✉️ **Email Verification** - Secure user registration with email verification
- 🔍 **City Search** - Search and find cities across Poland

### Admin Dashboard
- 📊 **Real-Time Monitoring** - Live user activity tracking via WebSockets
- 📈 **Statistics** - View total events, unique users, and event types
- 🎨 **Rich CLI Interface** - Beautiful terminal UI with color coding
- ⚡ **Auto-Reconnect** - Automatic reconnection on connection loss
- 🔔 **Activity Levels** - Info, Warning, and Error level tracking

### Backend
- 🚀 **FastAPI** - High-performance async REST API
- 🔌 **WebSocket Support** - Real-time bidirectional communication
- 💾 **SQLite Database** - Lightweight data persistence
- 📧 **Email Service** - SMTP integration for verification emails
- 🔐 **Secure Authentication** - Token-based verification system

## 🏗️ Architecture

The project consists of three main services:

1. **Backend** (FastAPI) - REST API and WebSocket server
2. **Telegram Bot** (aiogram) - User-facing Telegram interface
3. **CLI Admin** (Rich + WebSockets) - Real-time monitoring dashboard

All services communicate through Docker networking and share a unified architecture.

## 🛠️ Tech Stack

### Backend
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- SQLite - Database
- WebSockets - Real-time communication
- SMTP - Email delivery

### Telegram Bot
- aiogram 3.x - Telegram Bot framework
- httpx - Async HTTP client
- loguru - Logging

### CLI Admin
- websockets - WebSocket client
- rich - Terminal UI framework
- asyncio - Async programming

### DevOps
- Docker & Docker Compose
- Python 3.11

## 📦 Prerequisites

Before you begin, ensure you have:

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Gmail account with App Password enabled

### Getting Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token provided

### Setting Up Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd weatherbot
```

### 2. Create Environment File

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration:

# Database
DATABASE_URL=sqlite:///./data/weather.db

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# Security
SECRET_KEY=your-secret-key-here-generate-random-string

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here


Copy the output and use it as `SECRET_KEY` in your `.env` file.

## ⚙️ Configuration

Replace the following values in your `.env` file:

- `MAIL_USERNAME` - Your Gmail address
- `MAIL_PASSWORD` - Your Gmail app password (16 characters, no spaces)
- `MAIL_FROM` - Your Gmail address (same as MAIL_USERNAME)
- `SECRET_KEY` - Generated random string (see step 3 above)
- `TELEGRAM_BOT_TOKEN` - Token from BotFather

## 🏃 Running the Application

### Start All Services (Backend + Telegram Bot)

```bash
docker-compose up -d --build
```

This command will:
- Build all Docker images
- Start backend on port 8000
- Start Telegram bot
- Create necessary volumes and networks
- Run everything in detached mode

### Start with Admin Dashboard

To run with real-time monitoring:

```bash
docker-compose --profile admin up --build
```

This includes everything plus the CLI admin dashboard.

### Run Only Specific Services

```bash
# Backend only
docker-compose up -d backend

# Backend + Bot
docker-compose up -d backend telegram-bot

# Admin dashboard (requires backend running)
docker-compose --profile admin up cli-admin
```

## 📊 Admin Dashboard

The admin dashboard provides real-time monitoring of user activities.

### Starting the Dashboard

```bash
docker-compose --profile admin up cli-admin
```

### Dashboard Features

- **Connection Status** - Shows if connected to backend (🟢/🔴)
- **Statistics Panel** - Total events, unique users, event counts by level
- **Activity Log** - Real-time scrolling log of user actions
- **Color Coding** - Info (white), Warning (yellow), Error (red)

### Monitored Events

- User commands (`/weather`, `/hourly`, `/tomorrow`)
- Weather requests (with city and temperature)
- City searches
- Registration and verification
- Errors and warnings

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/verify` - Verify email code
- `GET /api/v1/auth/user/{telegram_id}` - Get user info

### Weather
- `GET /api/v1/weather/search` - Search cities
- `POST /api/v1/weather/set-city` - Set default city
- `POST /api/v1/weather/forecast` - Get current weather
- `POST /api/v1/weather/hourly` - Get hourly forecast
- `POST /api/v1/weather/tomorrow` - Get tomorrow's forecast

### Admin
- `POST /api/logs/activity` - Log user activity
- `WS /ws/logs` - WebSocket for real-time logs

### API Documentation

Access interactive API docs at: `http://localhost:8000/docs`

## 📁 Project Structure

```
weatherbot/
├── backend/
│   ├── api/
│   │   ├── admin.py          # Admin endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── weather.py        # Weather endpoints
│   │   └── websocket.py      # WebSocket handler
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   └── smtp_client.py    # Email client
│   ├── services/
│   │   ├── auth_service.py   # Auth logic
│   │   ├── email_service.py  # Email logic
│   │   └── weather_service.py # Weather logic
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── database.py           # Database setup
│   ├── main.py              # FastAPI app
│   └── requirements.txt
├── telegram-bot/
│   ├── handlers/
│   │   ├── registration.py   # Registration flow
│   │   ├── settings.py       # User settings
│   │   └── weather.py        # Weather commands
│   ├── utils/
│   │   └── api_client.py     # Backend client
│   ├── bot.py               # Bot entry point
│   └── requirements.txt
├── cli-admin/
│   ├── admin.py             # Dashboard UI
│   ├── websocket_client.py  # WebSocket client
│   └── requirements.txt
├── docker-compose.yaml
├── .env
└── README.md
```

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build backend
```

### Bot not responding

```bash
# Check bot logs
docker-compose logs telegram-bot

# Verify token in .env file
# Restart bot
docker-compose restart telegram-bot
```

### Admin dashboard can't connect

```bash
# Make sure backend is running
docker-compose ps

# Check backend is on port 8000
curl http://localhost:8000/

# Restart admin
docker-compose --profile admin up cli-admin
```

### Database issues

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

### Network errors

```bash
# Clean up Docker networks
docker-compose down
docker network prune -f
docker-compose up -d --build
```

## 📝 Usage Examples

### User Flow

1. User starts bot: `/start`
2. Registers with email: `/register user@example.com`
3. Receives verification code via email
4. Verifies: `/verify 123456`
5. Sets default city: `/setcity Warsaw`
6. Checks weather: `/weather`
7. Views hourly: `/hourly`
8. Checks tomorrow: `/tomorrow`

### Admin Flow

1. Start admin dashboard
2. Monitor real-time user activity
3. See statistics update automatically
4. Filter by event levels (info/warning/error)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ for weather enthusiasts

## 🙏 Acknowledgments

- OpenWeatherMap API for weather data
- Telegram for bot platform
- FastAPI community
- Rich library for beautiful CLI

---

**Happy Weather Tracking! 🌤️**
```
