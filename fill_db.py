# fill_db.py

import os
import urllib.request
import database as db
from seed import SEED_GAMES

os.makedirs("images", exist_ok=True)


def safe_filename(title):
    """Превращает название в безопасное имя файла"""
    return "".join(c for c in title if c.isalnum() or c in " -_").strip()


def download_cover(title, url):
    """Скачивает обложку в images/ и возвращает путь (или пустую строку)"""
    filename = safe_filename(title) + ".jpg"
    path = os.path.join("images", filename)

    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"      ⏩ уже есть: {filename}")
        return path

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r, open(path, "wb") as f:
            f.write(r.read())
        print(f"      ✅ скачано: {filename}")
        return path
    except Exception as e:
        print(f"      ❌ не скачалось: {e}")
        return ""


def main():
    db.init_db()
    count = db.count_games()

    if count > 0:
        print(f"⚠ В базе уже {count} игр.")
        print("Чтобы залить заново — выполни в MySQL:")
        print("  USE game_vault; DELETE FROM games;")
        print("Затем снова: python fill_db.py")
        return

    print(f"🎮 Заливаю {len(SEED_GAMES)} игр с обложками...\n")

    for i, g in enumerate(SEED_GAMES, 1):
        title = g[0]
        cover_url = g[9]
        data = g[:9]   # без URL

        print(f"  [{i}/{len(SEED_GAMES)}] {title}")
        cover_path = download_cover(title, cover_url)

        db.add_game(*data, cover_path)

    print(f"\n✅ Готово! Теперь в базе: {db.count_games()} игр")


if __name__ == "__main__":
    main()