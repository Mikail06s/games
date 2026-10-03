# database.py
# SQLite — встроенная база, не требует установки MySQL.
# Файл games.db создаётся автоматически рядом с .exe (или main.py).

import sqlite3
import os
import sys


def get_db_path():
    """Путь к файлу БД рядом с .exe (или main.py)"""
    if getattr(sys, "frozen", False):
        # Запущено как .exe
        base = os.path.dirname(sys.executable)
    else:
        # Запущено как .py
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "games.db")


DB_PATH = get_db_path()


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            studio TEXT,
            genre TEXT,
            platform TEXT,
            year INTEGER,
            rating REAL,
            hours REAL,
            status TEXT,
            progress INTEGER DEFAULT 0,
            cover_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_game(title, studio, genre, platform, year, rating, hours,
             status, progress, cover_path=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO games (title, studio, genre, platform, year, rating,
                           hours, status, progress, cover_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, studio, genre, platform, year, rating,
          hours, status, progress, cover_path))
    conn.commit()
    conn.close()


def get_games(order_by="title", search="", status=None, genre=None):
    allowed = {"title", "year", "rating", "hours", "genre", "status"}
    if order_by not in allowed:
        order_by = "title"

    q = "SELECT * FROM games WHERE (title LIKE ? OR studio LIKE ?)"
    params = [f"%{search}%", f"%{search}%"]

    if status:
        q += " AND status = ?"
        params.append(status)
    if genre:
        q += " AND genre = ?"
        params.append(genre)

    q += f" ORDER BY {order_by}"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE id=?", (game_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_game(game_id, title, studio, genre, platform, year, rating,
                hours, status, progress, cover_path=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE games SET title=?, studio=?, genre=?, platform=?, year=?,
                         rating=?, hours=?, status=?, progress=?, cover_path=?
        WHERE id=?
    """, (title, studio, genre, platform, year, rating,
          hours, status, progress, cover_path, game_id))
    conn.commit()
    conn.close()


def delete_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM games WHERE id=?", (game_id,))
    conn.commit()
    conn.close()


def count_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM games")
    n = cur.fetchone()[0]
    conn.close()
    return n


def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(hours), AVG(rating) FROM games")
    total = cur.fetchone()
    cur.execute("SELECT status, COUNT(*) FROM games GROUP BY status")
    by_status = cur.fetchall()
    cur.execute("SELECT genre, COUNT(*) FROM games GROUP BY genre")
    by_genre = cur.fetchall()
    cur.execute("SELECT title, hours FROM games ORDER BY hours DESC LIMIT 5")
    top_hours = cur.fetchall()
    conn.close()
    return total, by_status, by_genre, top_hours


def get_all_genres():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT genre FROM games "
                "WHERE genre IS NOT NULL AND genre != ''")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return sorted(rows)


def get_wishlist():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE status='хочу купить' ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return rows