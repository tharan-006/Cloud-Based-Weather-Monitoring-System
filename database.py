import sqlite3
from datetime import datetime, timezone
from config import Config

def get_db_connection():
    """Establish and return a SQLite database connection with row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the search_history table if it does not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            country TEXT,
            temp_c REAL,
            condition TEXT,
            description TEXT,
            icon TEXT,
            humidity INTEGER,
            wind_speed REAL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_search(city_name, country="", temp_c=None, condition="", description="", icon="", humidity=None, wind_speed=None):
    """
    Insert a city search record into the database.
    Returns the id of the newly inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO search_history 
        (city_name, country, temp_c, condition, description, icon, humidity, wind_speed, searched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city_name.strip().title(),
        country.strip().upper() if country else "",
        round(temp_c, 1) if temp_c is not None else None,
        condition,
        description,
        icon,
        humidity,
        round(wind_speed, 1) if wind_speed is not None else None,
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_history(limit=10):
    """
    Retrieve the most recent searches from the database.
    Returns a list of dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, city_name, country, temp_c, condition, description, icon, humidity, wind_speed, searched_at
        FROM search_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_search(search_id):
    """Delete a single search record by ID. Returns True if deleted."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history WHERE id = ?", (search_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_history():
    """Clear all records from search_history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()
    return True

def get_search_stats():
    """Get aggregate search statistics for dashboard insights."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_searches FROM search_history")
    total = cursor.fetchone()["total_searches"]

    cursor.execute("""
        SELECT city_name, country, COUNT(*) as count 
        FROM search_history 
        GROUP BY city_name, country 
        ORDER BY count DESC 
        LIMIT 5
    """)
    top_cities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "total_searches": total,
        "top_cities": top_cities
    }
