import requests
from datetime import datetime, timezone
import random
import hashlib
from config import Config

# Condition mappings for icons and descriptions
WEATHER_ICON_MAP = {
    "01d": {"fa": "fa-sun", "label": "Clear Sky (Day)", "color": "#f59e0b"},
    "01n": {"fa": "fa-moon", "label": "Clear Sky (Night)", "color": "#cbd5e1"},
    "02d": {"fa": "fa-cloud-sun", "label": "Few Clouds", "color": "#38bdf8"},
    "02n": {"fa": "fa-cloud-moon", "label": "Few Clouds (Night)", "color": "#94a3b8"},
    "03d": {"fa": "fa-cloud", "label": "Scattered Clouds", "color": "#93c5fd"},
    "03n": {"fa": "fa-cloud", "label": "Scattered Clouds", "color": "#94a3b8"},
    "04d": {"fa": "fa-cloud-meatball", "label": "Broken Clouds", "color": "#64748b"},
    "04n": {"fa": "fa-cloud-meatball", "label": "Overcast", "color": "#64748b"},
    "09d": {"fa": "fa-cloud-showers-heavy", "label": "Shower Rain", "color": "#0ea5e9"},
    "09n": {"fa": "fa-cloud-showers-heavy", "label": "Shower Rain", "color": "#0284c7"},
    "10d": {"fa": "fa-cloud-sun-rain", "label": "Rain", "color": "#38bdf8"},
    "10n": {"fa": "fa-cloud-moon-rain", "label": "Rain", "color": "#38bdf8"},
    "11d": {"fa": "fa-bolt-lightning", "label": "Thunderstorm", "color": "#eab308"},
    "11n": {"fa": "fa-bolt-lightning", "label": "Thunderstorm", "color": "#eab308"},
    "13d": {"fa": "fa-snowflake", "label": "Snow", "color": "#e0f2fe"},
    "13n": {"fa": "fa-snowflake", "label": "Snow", "color": "#e0f2fe"},
    "50d": {"fa": "fa-smog", "label": "Mist / Fog", "color": "#cbd5e1"},
    "50n": {"fa": "fa-smog", "label": "Mist / Fog", "color": "#cbd5e1"},
}

def get_icon_details(icon_code):
    """Return FontAwesome icon class and color for a given OpenWeather icon code."""
    return WEATHER_ICON_MAP.get(icon_code, {
        "fa": "fa-cloud",
        "label": "Weather",
        "color": "#38bdf8"
    })

def format_timestamp(ts, tz_offset=0, fmt="%I:%M %p"):
    """Convert Unix timestamp and timezone offset to readable formatted time string."""
    try:
        dt = datetime.fromtimestamp(ts + tz_offset, tz=timezone.utc)
        return dt.strftime(fmt)
    except Exception:
        return "--:--"

class WeatherService:
    """Service to handle OpenWeather API requests and data transformation."""

    @staticmethod
    def get_api_key():
        """Retrieve current API key from Config or environment."""
        return Config.OPENWEATHER_API_KEY.strip()

    @classmethod
    def fetch_weather(cls, city=None, lat=None, lon=None, custom_api_key=None):
        """
        Fetch current weather and 5-day forecast for a city or coordinates.
        Returns a dict: {"success": bool, "data": dict, "error": str, "is_simulated": bool}
        """
        api_key = custom_api_key.strip() if custom_api_key else cls.get_api_key()

        # If no API key is configured or is a template placeholder, fallback to simulated data
        if not api_key or api_key == "your_openweather_api_key_here":
            return cls._generate_simulated_weather(city=city, lat=lat, lon=lon)

        params_current = {"appid": api_key, "units": "metric"}
        params_forecast = {"appid": api_key, "units": "metric"}

        if city:
            params_current["q"] = city.strip()
            params_forecast["q"] = city.strip()
        elif lat is not None and lon is not None:
            params_current["lat"] = lat
            params_current["lon"] = lon
            params_forecast["lat"] = lat
            params_forecast["lon"] = lon
        else:
            return {"success": False, "error": "City name or coordinates must be provided."}

        try:
            # 1. Fetch current weather
            curr_resp = requests.get(Config.CURRENT_WEATHER_URL, params=params_current, timeout=8)
            
            if curr_resp.status_code == 404:
                return {
                    "success": False,
                    "error": f"City '{city}' not found. Please verify spelling and try again."
                }
            elif curr_resp.status_code == 401:
                # API key invalid or not yet activated by OpenWeather (takes up to 1-2 hours)
                sim_res = cls._generate_simulated_weather(city=city, lat=lat, lon=lon)
                sim_res["notice"] = "OpenWeather API key was rejected (401 Unauthorized - keys often take 1-2 hours to activate after signup). Showing simulated cloud data."
                return sim_res
            elif curr_resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"OpenWeather API Error ({curr_resp.status_code}): {curr_resp.json().get('message', 'Service error')}"
                }

            curr_data = curr_resp.json()

            # 2. Fetch 5-day forecast
            fore_resp = requests.get(Config.FORECAST_URL, params=params_forecast, timeout=8)
            forecast_data = fore_resp.json() if fore_resp.status_code == 200 else None

            # 3. Format and process data
            formatted = cls._format_weather_data(curr_data, forecast_data)
            return {
                "success": True,
                "data": formatted,
                "is_simulated": False,
                "source": "OpenWeatherMap Live Cloud API"
            }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request to weather service timed out. Please check your internet connection."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Failed to connect to weather server. Check your network connection."}
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

    @classmethod
    def _format_weather_data(cls, curr, fore):
        """Transform raw OpenWeather JSON into a structured, clean payload."""
        weather_item = curr.get("weather", [{}])[0]
        icon_code = weather_item.get("icon", "01d")
        icon_meta = get_icon_details(icon_code)
        tz_offset = curr.get("timezone", 0)

        # Wind speed from OpenWeather is in m/s; convert to km/h as well
        wind_speed_ms = curr.get("wind", {}).get("speed", 0.0)
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1)

        result = {
            "city": curr.get("name", "Unknown"),
            "country": curr.get("sys", {}).get("country", ""),
            "coordinates": {
                "lat": curr.get("coord", {}).get("lat"),
                "lon": curr.get("coord", {}).get("lon")
            },
            "current": {
                "temp_c": round(curr.get("main", {}).get("temp", 0), 1),
                "temp_f": round(curr.get("main", {}).get("temp", 0) * 9/5 + 32, 1),
                "feels_like_c": round(curr.get("main", {}).get("feels_like", 0), 1),
                "feels_like_f": round(curr.get("main", {}).get("feels_like", 0) * 9/5 + 32, 1),
                "temp_min_c": round(curr.get("main", {}).get("temp_min", 0), 1),
                "temp_max_c": round(curr.get("main", {}).get("temp_max", 0), 1),
                "condition": weather_item.get("main", "Clear"),
                "description": weather_item.get("description", "").title(),
                "icon": icon_code,
                "icon_url": f"https://openweathermap.org/img/wn/{icon_code}@4x.png",
                "icon_fa": icon_meta["fa"],
                "icon_color": icon_meta["color"],
                "humidity": curr.get("main", {}).get("humidity", 0),
                "pressure": curr.get("main", {}).get("pressure", 1013),
                "visibility_km": round(curr.get("visibility", 10000) / 1000, 1),
                "wind_speed_kmh": wind_speed_kmh,
                "wind_speed_ms": round(wind_speed_ms, 1),
                "wind_deg": curr.get("wind", {}).get("deg", 0),
                "clouds": curr.get("clouds", {}).get("all", 0),
                "sunrise": format_timestamp(curr.get("sys", {}).get("sunrise", 0), tz_offset),
                "sunset": format_timestamp(curr.get("sys", {}).get("sunset", 0), tz_offset),
                "local_time": format_timestamp(curr.get("dt", 0), tz_offset, fmt="%A, %B %d, %Y • %I:%M %p")
            },
            "forecast_5day": [],
            "hourly_24h": []
        }

        # Process 5-day forecast
        if fore and "list" in fore:
            result["forecast_5day"] = cls._process_daily_forecast(fore["list"], tz_offset)
            result["hourly_24h"] = cls._process_hourly_forecast(fore["list"], tz_offset)

        return result

    @classmethod
    def _process_daily_forecast(cls, forecast_list, tz_offset):
        """Aggregate 3-hour forecast timestamps into 5 distinct daily forecasts."""
        from collections import defaultdict
        daily_groups = defaultdict(list)

        for item in forecast_list:
            dt = datetime.fromtimestamp(item.get("dt", 0) + tz_offset, tz=timezone.utc)
            date_key = dt.strftime("%Y-%m-%d")
            daily_groups[date_key].append(item)

        forecast_cards = []
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for date_key, items in sorted(daily_groups.items()):
            # We skip today's remaining hours if already evening or keep the next 5 days
            if len(forecast_cards) >= 5:
                break

            temps = [x.get("main", {}).get("temp", 0) for x in items]
            min_temp = round(min(temps), 1)
            max_temp = round(max(temps), 1)
            
            # Pick mid-day item (approx 12:00 or middle element) for representative weather condition
            mid_item = items[len(items) // 2]
            w = mid_item.get("weather", [{}])[0]
            icon_code = w.get("icon", "01d")
            # Ensure day icon for daily forecast
            if icon_code.endswith("n"):
                icon_code = icon_code[:-1] + "d"
            icon_meta = get_icon_details(icon_code)

            dt_obj = datetime.strptime(date_key, "%Y-%m-%d")
            day_name = dt_obj.strftime("%A")
            formatted_date = dt_obj.strftime("%b %d")

            humidities = [x.get("main", {}).get("humidity", 0) for x in items]
            avg_humidity = round(sum(humidities) / len(humidities)) if humidities else 50
            avg_wind = round((sum(x.get("wind", {}).get("speed", 0) for x in items) / len(items)) * 3.6, 1) if items else 0.0

            pop = round(max([x.get("pop", 0) for x in items]) * 100)

            forecast_cards.append({
                "date": date_key,
                "day_name": day_name,
                "formatted_date": formatted_date,
                "temp_min_c": min_temp,
                "temp_max_c": max_temp,
                "temp_min_f": round(min_temp * 9/5 + 32, 1),
                "temp_max_f": round(max_temp * 9/5 + 32, 1),
                "condition": w.get("main", "Clear"),
                "description": w.get("description", "").title(),
                "icon": icon_code,
                "icon_url": f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                "icon_fa": icon_meta["fa"],
                "icon_color": icon_meta["color"],
                "humidity": avg_humidity,
                "wind_speed_kmh": avg_wind,
                "rain_prob": pop
            })

        return forecast_cards

    @classmethod
    def _process_hourly_forecast(cls, forecast_list, tz_offset, max_points=8):
        """Extract the next 24 hours of 3-hour forecasts."""
        hourly = []
        for item in forecast_list[:max_points]:
            dt = datetime.fromtimestamp(item.get("dt", 0) + tz_offset, tz=timezone.utc)
            w = item.get("weather", [{}])[0]
            icon_code = w.get("icon", "01d")
            icon_meta = get_icon_details(icon_code)
            temp = round(item.get("main", {}).get("temp", 0), 1)

            hourly.append({
                "time": dt.strftime("%I %p"),
                "temp_c": temp,
                "temp_f": round(temp * 9/5 + 32, 1),
                "condition": w.get("main", "Clear"),
                "icon": icon_code,
                "icon_fa": icon_meta["fa"],
                "icon_color": icon_meta["color"],
                "pop": round(item.get("pop", 0) * 100)
            })
        return hourly

    @classmethod
    def _generate_simulated_weather(cls, city=None, lat=None, lon=None):
        """
        Generate realistic simulated weather data for presentation / demo purposes
        when an OpenWeather API key is not yet set or pending activation.
        Uses deterministic seeding based on city name so repeated searches are consistent.
        """
        city_name = city.strip().title() if city else "Cloud City"
        
        # Deterministic seed based on city name
        h = int(hashlib.md5(city_name.encode()).hexdigest(), 16)
        rng = random.Random(h)

        # Preset climates for common sample cities
        sample_profiles = {
            "London": {"country": "GB", "base_temp": 15, "condition": "Rain", "desc": "light rain", "icon": "10d", "hum": 78, "wind": 18},
            "New York": {"country": "US", "base_temp": 19, "condition": "Clouds", "desc": "broken clouds", "icon": "04d", "hum": 62, "wind": 15},
            "Tokyo": {"country": "JP", "base_temp": 22, "condition": "Clear", "desc": "clear sky", "icon": "01d", "hum": 55, "wind": 10},
            "Paris": {"country": "FR", "base_temp": 17, "condition": "Clouds", "desc": "scattered clouds", "icon": "03d", "hum": 65, "wind": 12},
            "Dubai": {"country": "AE", "base_temp": 34, "condition": "Clear", "desc": "sunny & clear", "icon": "01d", "hum": 40, "wind": 14},
            "Mumbai": {"country": "IN", "base_temp": 30, "condition": "Clouds", "desc": "few clouds", "icon": "02d", "hum": 75, "wind": 11},
            "Sydney": {"country": "AU", "base_temp": 21, "condition": "Clear", "desc": "sunny", "icon": "01d", "hum": 58, "wind": 16},
            "Singapore": {"country": "SG", "base_temp": 29, "condition": "Thunderstorm", "desc": "tropical thunderstorm", "icon": "11d", "hum": 84, "wind": 8},
        }

        profile = sample_profiles.get(city_name)
        if not profile:
            # Deterministic generation for any arbitrary city
            conditions = [
                ("Clear", "clear sky", "01d", 18 + (h % 15)),
                ("Clouds", "scattered clouds", "03d", 14 + (h % 12)),
                ("Rain", "moderate rain", "10d", 12 + (h % 10)),
                ("Clouds", "few clouds", "02d", 20 + (h % 10)),
                ("Thunderstorm", "thunderstorm with rain", "11d", 22 + (h % 8)),
                ("Snow", "light snow", "13d", -2 + (h % 6)),
            ]
            chosen = conditions[h % len(conditions)]
            profile = {
                "country": "CLOUD",
                "base_temp": chosen[3],
                "condition": chosen[0],
                "desc": chosen[1],
                "icon": chosen[2],
                "hum": 45 + (h % 45),
                "wind": 5 + (h % 25)
            }

        temp_c = profile["base_temp"]
        icon_meta = get_icon_details(profile["icon"])

        # Create simulated 5-day forecast
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        now = datetime.now()
        current_day_idx = now.weekday()

        forecast_5day = []
        variations = [
            ("Clouds", "scattered clouds", "03d", 1, -2),
            ("Clear", "clear sky", "01d", 2, 1),
            ("Rain", "light rain", "10d", -1, -3),
            ("Clouds", "broken clouds", "04d", 0, -1),
            ("Clear", "sunny", "01d", 3, 0)
        ]

        for i in range(1, 6):
            future_dt = now.replace(day=now.day)  # representation
            day_name = days[(current_day_idx + i) % 7]
            v = variations[(h + i) % len(variations)]
            max_t = round(temp_c + v[3] + rng.randint(-1, 2), 1)
            min_t = round(max_t - 5 - rng.randint(0, 3), 1)
            f_icon_meta = get_icon_details(v[2])

            forecast_5day.append({
                "date": f"2026-10-{25+i:02d}",
                "day_name": day_name,
                "formatted_date": f"Oct {25+i}",
                "temp_min_c": min_t,
                "temp_max_c": max_t,
                "temp_min_f": round(min_t * 9/5 + 32, 1),
                "temp_max_f": round(max_t * 9/5 + 32, 1),
                "condition": v[0],
                "description": v[1].title(),
                "icon": v[2],
                "icon_url": f"https://openweathermap.org/img/wn/{v[2]}@2x.png",
                "icon_fa": f_icon_meta["fa"],
                "icon_color": f_icon_meta["color"],
                "humidity": min(95, max(30, profile["hum"] + rng.randint(-15, 15))),
                "wind_speed_kmh": round(max(3, profile["wind"] + rng.randint(-4, 6)), 1),
                "rain_prob": rng.randint(10, 85)
            })

        # Create 24h hourly forecast
        hourly_24h = []
        hours = ["12 PM", "03 PM", "06 PM", "09 PM", "12 AM", "03 AM", "06 AM", "09 AM"]
        for idx, hr in enumerate(hours):
            h_temp = round(temp_c + (2 if idx in (0, 1, 7) else -3), 1)
            hourly_24h.append({
                "time": hr,
                "temp_c": h_temp,
                "temp_f": round(h_temp * 9/5 + 32, 1),
                "condition": profile["condition"],
                "icon": profile["icon"],
                "icon_fa": icon_meta["fa"],
                "icon_color": icon_meta["color"],
                "pop": rng.randint(5, 60)
            })

        data = {
            "city": city_name,
            "country": profile["country"],
            "coordinates": {"lat": round(15.0 + (h % 40), 2), "lon": round(-20.0 + (h % 80), 2)},
            "current": {
                "temp_c": round(temp_c, 1),
                "temp_f": round(temp_c * 9/5 + 32, 1),
                "feels_like_c": round(temp_c + rng.randint(-2, 2), 1),
                "feels_like_f": round((temp_c + 1) * 9/5 + 32, 1),
                "temp_min_c": round(temp_c - 3.5, 1),
                "temp_max_c": round(temp_c + 3.2, 1),
                "condition": profile["condition"],
                "description": profile["desc"].title(),
                "icon": profile["icon"],
                "icon_url": f"https://openweathermap.org/img/wn/{profile['icon']}@4x.png",
                "icon_fa": icon_meta["fa"],
                "icon_color": icon_meta["color"],
                "humidity": profile["hum"],
                "pressure": 1012 + (h % 8),
                "visibility_km": 10.0,
                "wind_speed_kmh": round(profile["wind"] * 1.0, 1),
                "wind_speed_ms": round(profile["wind"] / 3.6, 1),
                "wind_deg": (h * 45) % 360,
                "clouds": 35 if "Clouds" in profile["condition"] else (10 if "Clear" in profile["condition"] else 80),
                "sunrise": "06:22 AM",
                "sunset": "06:48 PM",
                "local_time": datetime.now().strftime("%A, %B %d, %Y • %I:%M %p")
            },
            "forecast_5day": forecast_5day,
            "hourly_24h": hourly_24h
        }

        return {
            "success": True,
            "data": data,
            "is_simulated": True,
            "source": "Simulated Weather Engine (Add OpenWeather API key to .env for Live Cloud API)"
        }
