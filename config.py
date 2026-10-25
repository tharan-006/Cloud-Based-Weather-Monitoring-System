import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "cloud-weather-default-secret-key-2026")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "weather_history.db"))
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # OpenWeather API Endpoints
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    CURRENT_WEATHER_URL = f"{OPENWEATHER_BASE_URL}/weather"
    FORECAST_URL = f"{OPENWEATHER_BASE_URL}/forecast"
