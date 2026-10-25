import os
from flask import Flask, render_template, request, jsonify
from config import Config
from database import init_db, add_search, get_history, delete_search, clear_history, get_search_stats
from weather_service import WeatherService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLite database schema
init_db()

@app.route("/")
def index():
    """Render the main weather dashboard page."""
    api_configured = bool(Config.OPENWEATHER_API_KEY and Config.OPENWEATHER_API_KEY != "your_openweather_api_key_here")
    return render_template("index.html", api_configured=api_configured)

@app.route("/api/weather", methods=["GET"])
def get_weather():
    """
    Search weather for a specified city name.
    Query parameter: city (string)
    """
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({
            "success": False,
            "error": "City name is required. Please type a city name."
        }), 400

    if len(city) < 2:
        return jsonify({
            "success": False,
            "error": "City name must be at least 2 characters long."
        }), 400

    # Fetch weather data
    result = WeatherService.fetch_weather(city=city)

    if result.get("success"):
        weather_data = result["data"]
        curr = weather_data["current"]
        
        # Save to SQLite search history
        try:
            add_search(
                city_name=weather_data.get("city", city),
                country=weather_data.get("country", ""),
                temp_c=curr.get("temp_c"),
                condition=curr.get("condition"),
                description=curr.get("description"),
                icon=curr.get("icon"),
                humidity=curr.get("humidity"),
                wind_speed=curr.get("wind_speed_kmh")
            )
        except Exception as e:
            app.logger.error(f"Failed to record search history: {e}")

        return jsonify(result)
    else:
        return jsonify(result), 404 if "not found" in result.get("error", "").lower() else 500

@app.route("/api/weather/coords", methods=["GET"])
def get_weather_by_coords():
    """
    Fetch weather for geographic latitude and longitude coordinates.
    Query parameters: lat (float), lon (float)
    """
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Valid latitude and longitude coordinates are required."
        }), 400

    result = WeatherService.fetch_weather(lat=lat, lon=lon)

    if result.get("success"):
        weather_data = result["data"]
        curr = weather_data["current"]
        
        try:
            add_search(
                city_name=weather_data.get("city", "Current Location"),
                country=weather_data.get("country", ""),
                temp_c=curr.get("temp_c"),
                condition=curr.get("condition"),
                description=curr.get("description"),
                icon=curr.get("icon"),
                humidity=curr.get("humidity"),
                wind_speed=curr.get("wind_speed_kmh")
            )
        except Exception as e:
            app.logger.error(f"Failed to record search history: {e}")

        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route("/api/history", methods=["GET"])
def api_get_history():
    """Return the 10 most recent search history records."""
    limit = request.args.get("limit", default=10, type=int)
    history = get_history(limit=limit)
    return jsonify({
        "success": True,
        "history": history
    })

@app.route("/api/history/<int:search_id>", methods=["DELETE"])
def api_delete_history(search_id):
    """Delete a single search record by ID."""
    deleted = delete_search(search_id)
    if deleted:
        return jsonify({"success": True, "message": "Search record removed."})
    return jsonify({"success": False, "error": "Record not found."}), 404

@app.route("/api/history", methods=["DELETE"])
def api_clear_history():
    """Clear all search history."""
    clear_history()
    return jsonify({"success": True, "message": "Search history cleared."})

@app.route("/api/status", methods=["GET"])
def api_status():
    """Return cloud application status, API configuration, and database stats."""
    has_api_key = bool(Config.OPENWEATHER_API_KEY and Config.OPENWEATHER_API_KEY != "your_openweather_api_key_here")
    stats = get_search_stats()
    return jsonify({
        "status": "healthy",
        "service": "Cloud-Based Weather Monitoring System",
        "api_configured": has_api_key,
        "database": "SQLite active",
        "stats": stats
    })

@app.route("/api/settings/key", methods=["POST"])
def api_update_key():
    """
    Test and temporarily update API key for current session.
    Body JSON: {"api_key": "..."}
    """
    data = request.get_json(silent=True) or {}
    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"success": False, "error": "API key cannot be empty."}), 400

    # Test key with a sample query to OpenWeather
    test_res = WeatherService.fetch_weather(city="London", custom_api_key=api_key)
    
    if test_res.get("success") and not test_res.get("is_simulated"):
        # Update current runtime config
        Config.OPENWEATHER_API_KEY = api_key
        return jsonify({
            "success": True,
            "message": "OpenWeather API Key verified and activated successfully!"
        })
    else:
        err = test_res.get("error") or test_res.get("notice") or "API key validation failed. Please verify the key."
        return jsonify({
            "success": False,
            "error": err
        }), 400

if __name__ == "__main__":
    print(f"Starting Cloud-Based Weather Monitoring System on port {Config.PORT}...")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
