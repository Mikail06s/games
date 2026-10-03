# database.py
import mysql.connector
# database.py
import mysql.connector
from mysql.connector.locales.eng import client_error   # ← ДОБАВЬ ЭТУ СТРОКУ
from config import DB_CONFIG
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            studio VARCHAR(255),
            genre VARCHAR(100),
            platform VARCHAR(50),
            year INT,
            rating FLOAT,
            hours FLOAT,
            status VARCHAR(50),
            progress INT DEFAULT 0,
            cover_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    cur.close()
    conn.close()


def add_game(title, studio, genre, platform, year, rating, hours,
             status, progress, cover_path=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO games (title, studio, genre, platform, year, rating,
                           hours, status, progress, cover_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (title, studio, genre, platform, year, rating,
          hours, status, progress, cover_path))
    conn.commit()
    cur.close()
    conn.close()


def get_games(order_by="title", search="", status=None, genre=None):
    allowed = {"title", "year", "rating", "hours", "genre", "status"}
    if order_by not in allowed:
        order_by = "title"

    q = "SELECT * FROM games WHERE (title LIKE %s OR studio LIKE %s)"
    params = [f"%{search}%", f"%{search}%"]

    if status:
        q += " AND status = %s"
        params.append(status)
    if genre:
        q += " AND genre = %s"
        params.append(genre)

    q += f" ORDER BY {order_by}"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(q, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE id=%s", (game_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def update_game(game_id, title, studio, genre, platform, year, rating,
                hours, status, progress, cover_path=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE games SET title=%s, studio=%s, genre=%s, platform=%s, year=%s,
                         rating=%s, hours=%s, status=%s, progress=%s, cover_path=%s
        WHERE id=%s
    """, (title, studio, genre, platform, year, rating,
          hours, status, progress, cover_path, game_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM games WHERE id=%s", (game_id,))
    conn.commit()
    cur.close()
    conn.close()


def count_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM games")
    n = cur.fetchone()[0]
    cur.close()
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
    cur.close()
    conn.close()
    return total, by_status, by_genre, top_hours


def get_all_genres():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT genre FROM games "
                "WHERE genre IS NOT NULL AND genre != ''")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return sorted(rows)


def get_wishlist():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE status='хочу купить' ORDER BY title")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows