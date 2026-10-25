# Cloud-Based Weather Monitoring System

A modern, responsive, and resilient **Cloud-Based Weather Monitoring System** developed for **Cloud Computing**. This application allows users to check current global meteorological conditions and 5-day forecasts for any city, backed by an SQLite cloud persistence layer and integrated with the OpenWeatherMap REST API.

---

## 🌤️ System Highlights & Features

1. **City Search & Real-Time Weather:**
   - Search any city globally to fetch live weather data.
   - Quick-select chips for major global cities (*London, New York, Tokyo, Paris, Dubai, Mumbai, Singapore, Sydney*).
   - Instant geolocation support (*"Use Current Location"* using HTML5 Geolocation API).
2. **Current Temperature:**
   - Precision temperature in Celsius (°C) with real-time toggle to Fahrenheit (°F).
   - "Feels like" temperature, daily high, and daily low readings.
3. **Atmospheric & Weather Conditions:**
   - Real-time condition display (*Clear/Sunny, Clouds, Rain, Thunderstorm, Mist/Fog, Snow*).
   - High-resolution weather icons with smooth floating animations.
4. **Comprehensive Meteorological Telemetry:**
   - **Humidity:** Percentage with dynamic comfort scale indicator (*Dry, Comfortable, Muggy*).
   - **Wind Speed:** Speed in km/h and m/s, accompanied by an interactive compass showing degree and cardinal direction (*e.g., 180° S*).
   - **Atmospheric Pressure:** Real-time barometric pressure in hPa.
   - **Visibility:** Distance in kilometers.
   - **Sunrise & Sunset:** Local astronomical times.
   - **Cloud Coverage:** Cloudiness percentage.
5. **Weather Forecasting:**
   - **24-Hour Atmospheric Timeline:** 3-hour interval progression of upcoming temperatures and precipitation probabilities.
   - **5-Day Meteorological Forecast Cards:** Day-by-day forecast cards showing high/low temperatures, representative weather condition, rain probability, and humidity.
6. **SQLite Persistent Search History:**
   - Automatic recording of all searched cities, countries, temperatures, conditions, and timestamps into a local SQLite database (`weather_history.db`).
   - One-click re-search from the history panel.
   - Delete individual search records or clear the entire history.
7. **Cloud Architecture & Resilience:**
   - **12-Factor App Configuration:** API keys and environment variables strictly managed via `.env`.
   - **Dual-Engine Operation:** Direct integration with live **OpenWeatherMap REST API**, coupled with an automated deterministic simulation fallback engine so the application functions even when an API key is pending activation or offline.
   - **In-App API Key Manager:** Modal to test and activate an OpenWeather API key directly from the browser without server restarts.
8. **Modern Dark Blue & White UI:**
   - Built with **Bootstrap 5.3**, custom CSS glassmorphism, glowing accents (`#38BDF8`), and Google Fonts (*Outfit* and *Plus Jakarta Sans*).
   - Fully responsive across desktop, tablet, and mobile screens.
9. **Robust Error Handling:**
   - User-friendly alerts for unknown city names (404), network timeouts, and invalid API keys.

---

## 🏛️ Cloud Architecture Overview

```
                      +---------------------------------------+
                      |       Client Tier (Browser)           |
                      |  HTML5, Vanilla CSS, JS, Bootstrap 5  |
                      +-------------------+-------------------+
                                          |
                                HTTP REST / JSON
                                          |
                                          v
                      +---------------------------------------+
                      |      Application Tier (PaaS/IaaS)     |
                      |          Python 3 + Flask             |
                      |  - Router & Controller (app.py)       |
                      |  - Service Adapter (weather_service)  |
                      |  - Security & Config (.env / config)  |
                      +---------+-------------------+---------+
                                |                   |
               Internal Storage |                   | External Cloud API
                                v                   v
          +-----------------------+       +-------------------------+
          | Cloud Persistence     |       | External SaaS / Cloud   |
          | SQLite DB (History)   |       | OpenWeatherMap REST API |
          +-----------------------+       +-------------------------+
```

---

## 📁 Project Directory Structure

```
cloud 6/
│
├── app.py                     # Flask application entry point and REST API routes
├── config.py                  # App configuration & .env environment loader
├── database.py                # SQLite database management (init, search, delete history)
├── weather_service.py         # OpenWeather API integration & fallback simulation engine
├── requirements.txt           # Python dependencies (Flask, requests, python-dotenv, pytest)
├── .env                       # Local environment variables (Contains active settings)
├── .env.example               # Environment template for version control
├── .gitignore                 # Files excluded from git
├── .dockerignore              # Files excluded from Docker builds
├── Dockerfile                 # Container specification for Cloud deployment
├── Procfile                   # Process configuration for PaaS platforms (Heroku, Render)
├── README.md                  # Comprehensive documentation and project guide
│
├── static/
│   ├── css/
│   │   └── style.css          # Dark blue & white theme, glassmorphic styling, animations
│   └── js/
│       └── app.js             # Client-side controller (AJAX, DOM updates, history, units)
│
├── templates/
│   ├── base.html              # Base layout with navbar, clock, modals, and footer
│   └── index.html             # Weather dashboard layout, hero card, metrics, forecast
│
└── tests/
    └── test_weather.py        # Automated test suite (7 unit tests covering all components)
```

---

## 🔑 How to Obtain & Configure OpenWeather API Key

The application is fully wired to consume live data from the **OpenWeatherMap REST API**.

### Step 1: Sign Up for Free
1. Go to [OpenWeatherMap.org](https://openweathermap.org/) and create a free account.
2. Verify your email address.

### Step 2: Generate an API Key
1. Go to your account menu at the top-right and select **My API Keys** (or visit [https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys)).
2. Copy your default 32-character API key (or create a new key named `CloudWeather`).

> **Note on Activation:** Newly created OpenWeather keys generally take **30 to 60 minutes** to become active on global edge servers. During this window, OpenWeather returns a `401 Unauthorized` status until activation completes. Our system handles this gracefully with its fallback engine.

### Step 3: Configure the Key in Your Project
You can configure the key in either of two ways:

#### Option A: In the `.env` file (Recommended)
Open the `.env` file in the project root directory and paste your key:
```ini
OPENWEATHER_API_KEY=your_actual_32_character_key_here
PORT=5050
FLASK_DEBUG=True
```

#### Option B: Directly from the Dashboard UI
1. Launch the web application.
2. Click the **API Key** button in the top navbar.
3. Paste your key and click **Verify & Apply Key**. The application validates the key live against OpenWeather and switches to the live cloud stream immediately.

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14 installed.
- `pip` package manager.

### 1. Clone or Download the Project
```bash
cd "cloud 6"
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Run the Server
```bash
python app.py
```

The application starts on `http://127.0.0.1:5050` (or the port specified in `.env`).

### 5. Access the Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:5050
```

---

## 🧪 Running Automated Tests

A comprehensive unit test suite is included in `tests/test_weather.py`, testing:
- HTML template rendering.
- SQLite database transactions (create, insert, query, delete, and clear).
- Weather service data formatting and 5-day forecast processing.
- Input validation (empty city name, minimum character length).
- REST API history persistence.
- System health status endpoint.

Run the tests using Python's test runner:
```bash
python -m unittest discover -s tests -v
```

Expected output:
```
test_01_index_page (test_weather.WeatherAppTestCase) ... ok
test_02_database_operations (test_weather.WeatherAppTestCase) ... ok
test_03_weather_service_structure (test_weather.WeatherAppTestCase) ... ok
test_04_api_weather_validation (test_weather.WeatherAppTestCase) ... ok
test_05_api_weather_search_and_history_persistence (test_weather.WeatherAppTestCase) ... ok
test_06_api_history_deletion (test_weather.WeatherAppTestCase) ... ok
test_07_api_status (test_weather.WeatherAppTestCase) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.102s

OK
```

---

## ☁️ Cloud Deployment Guide

This project is built following **Cloud-Native & 12-Factor App principles** for presentation in a Cloud Computing course.

### Deployment Option 1: Docker Containerization
A production-ready `Dockerfile` is included.

1. Build the container image:
   ```bash
   docker build -t cloud-weather-app .
   ```
2. Run the container:
   ```bash
   docker run -p 5050:5050 -e OPENWEATHER_API_KEY="your_key" cloud-weather-app
   ```
3. Access at `http://localhost:5050`.

### Deployment Option 2: Render / Railway / Heroku (PaaS)
1. Push this repository to GitHub.
2. In **Render** or **Railway**, create a new **Web Service** connected to your repository.
3. Configure the build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the start command:
   ```bash
   python app.py
   ```
5. Add the environment variable `OPENWEATHER_API_KEY` under the service's Environment settings.

### Deployment Option 3: AWS Elastic Beanstalk / EC2
1. Launch an Amazon Linux 2023 EC2 instance or Elastic Beanstalk Python environment.
2. Clone the repository and install requirements.
3. Set up a systemd service or Gunicorn process with Nginx as a reverse proxy.

---

## 📡 REST API Reference

| Endpoint | Method | Parameters | Description |
|---|---|---|---|
| `/` | `GET` | None | Renders main weather dashboard |
| `/api/weather` | `GET` | `city` (string) | Fetches current weather + 5-day forecast and saves to SQLite |
| `/api/weather/coords` | `GET` | `lat` (float), `lon` (float) | Fetches weather for GPS coordinates |
| `/api/history` | `GET` | `limit` (default: 10) | Retrieves recent search history from SQLite |
| `/api/history/<id>` | `DELETE` | `id` (integer) | Deletes a specific history record |
| `/api/history` | `DELETE` | None | Clears all search history |
| `/api/status` | `GET` | None | Returns health check, API status, and search counts |
| `/api/settings/key` | `POST` | JSON: `{"api_key": "..."}` | Validates and updates API key live |

---

## 👥 Academic Project Attribution
- **Course:** Cloud Computing
- **Project:** Cloud-Based Weather Monitoring System
- **Technologies:** Python Flask, OpenWeather REST API, SQLite, HTML5, CSS3, JavaScript, Bootstrap 5
