# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os
import database as db

STATUSES = ["играю", "пройдено", "брошено", "хочу купить"]

COLORS = {
    "bg":       "#1e1e2e",
    "bg2":      "#282a3a",
    "bg3":      "#313244",
    "fg":       "#cdd6f4",
    "fg_dim":   "#a6adc8",
    "accent":   "#89b4fa",
    "accent2":  "#cba6f7",
    "success":  "#a6e3a1",
    "warning":  "#f9e2af",
    "danger":   "#f38ba8",
    "border":   "#45475a",
    "hover":    "#585b70",
    "select":   "#45475a",
}

STATUS_COLORS = {
    "играю":       COLORS["success"],
    "пройдено":    COLORS["accent"],
    "брошено":     COLORS["danger"],
    "хочу купить": COLORS["warning"],
}


class GameVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 GameVault — коллекция игр")
        self.root.geometry("1280x760")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1100, 650)

        db.init_db()

        self.selected_id = None
        self.preview_img = None

        self.setup_styles()
        self.build_ui()

        self.status_var.set("Все")
        self.genre_var.set("Все")
        self.sort_var.set("title")

        self.refresh_genres()
        self.load_data()

    # ---------- Стили ----------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TCombobox",
                        fieldbackground=COLORS["bg3"],
                        background=COLORS["bg3"],
                        foreground=COLORS["fg"],
                        arrowcolor=COLORS["accent"],
                        bordercolor=COLORS["border"],
                        lightcolor=COLORS["border"],
                        darkcolor=COLORS["border"],
                        insertcolor=COLORS["fg"],
                        padding=6)
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", COLORS["bg3"])],
                  foreground=[("readonly", COLORS["fg"])],
                  selectbackground=[("readonly", COLORS["accent"])],
                  selectforeground=[("readonly", COLORS["bg"])])

        style.configure("Dark.Treeview",
                        background=COLORS["bg2"],
                        fieldbackground=COLORS["bg2"],
                        foreground=COLORS["fg"],
                        bordercolor=COLORS["border"],
                        rowheight=30,
                        font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading",
                        background=COLORS["bg3"],
                        foreground=COLORS["accent"],
                        relief="flat",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)
        style.map("Dark.Treeview.Heading",
                  background=[("active", COLORS["hover"])])
        style.map("Dark.Treeview",
                  background=[("selected", COLORS["select"])],
                  foreground=[("selected", COLORS["accent"])])

        style.configure("Dark.Vertical.TScrollbar",
                        background=COLORS["bg3"],
                        troughcolor=COLORS["bg2"],
                        bordercolor=COLORS["bg2"],
                        arrowcolor=COLORS["fg_dim"],
                        relief="flat")
        style.map("Dark.Vertical.TScrollbar",
                  background=[("active", COLORS["accent"])])

    def make_button(self, parent, text, command, color=None):
        color = color or COLORS["accent"]
        btn = tk.Button(parent, text=text, command=command,
                        bg=COLORS["bg3"], fg=COLORS["fg"],
                        activebackground=color,
                        activeforeground=COLORS["bg"],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat", bd=0, padx=14, pady=8,
                        cursor="hand2",
                        highlightthickness=1,
                        highlightbackground=COLORS["border"],
                        highlightcolor=color)
        def on_enter(e): btn.config(bg=color, fg=COLORS["bg"])
        def on_leave(e): btn.config(bg=COLORS["bg3"], fg=COLORS["fg"])
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ---------- UI ----------
    def build_ui(self):
        # Заголовок
        header = tk.Frame(self.root, bg=COLORS["bg2"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🎮  GameVault", bg=COLORS["bg2"],
                 fg=COLORS["accent"], font=("Segoe UI", 20, "bold")
                 ).pack(side="left", padx=25)
        tk.Label(header, text="Коллекция игр", bg=COLORS["bg2"],
                 fg=COLORS["fg_dim"], font=("Segoe UI", 11)
                 ).pack(side="left", pady=(10, 0))

        # Фильтры
        filters = tk.Frame(self.root, bg=COLORS["bg"], pady=12)
        filters.pack(fill="x", padx=20)

        tk.Label(filters, text="🔍", bg=COLORS["bg"], fg=COLORS["fg_dim"],
                 font=("Segoe UI", 12)).pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_data())
        tk.Entry(filters, textvariable=self.search_var,
                 bg=COLORS["bg3"], fg=COLORS["fg"],
                 insertbackground=COLORS["fg"],
                 relief="flat", font=("Segoe UI", 10),
                 width=25, highlightthickness=1,
                 highlightbackground=COLORS["border"],
                 highlightcolor=COLORS["accent"]
                 ).pack(side="left", ipady=6, padx=(0, 15))

        tk.Label(filters, text="Статус:", bg=COLORS["bg"],
                 fg=COLORS["fg_dim"], font=("Segoe UI", 10)
                 ).pack(side="left", padx=(0, 5))
        self.status_var = tk.StringVar(value="Все")
        ttk.Combobox(filters, textvariable=self.status_var,
                     state="readonly", width=13,
                     values=["Все"] + STATUSES,
                     style="Dark.TCombobox").pack(side="left", padx=(0, 15))
        self.status_var.trace("w", lambda *a: self.load_data())

        tk.Label(filters, text="Жанр:", bg=COLORS["bg"],
                 fg=COLORS["fg_dim"], font=("Segoe UI", 10)
                 ).pack(side="left", padx=(0, 5))
        self.genre_var = tk.StringVar(value="Все")
        self.genre_combo = ttk.Combobox(filters, textvariable=self.genre_var,
                                        state="readonly", width=13,
                                        style="Dark.TCombobox")
        self.genre_combo.pack(side="left", padx=(0, 15))
        self.genre_var.trace("w", lambda *a: self.load_data())

        tk.Label(filters, text="Сортировка:", bg=COLORS["bg"],
                 fg=COLORS["fg_dim"], font=("Segoe UI", 10)
                 ).pack(side="left", padx=(0, 5))
        self.sort_var = tk.StringVar(value="title")
        ttk.Combobox(filters, textvariable=self.sort_var,
                     state="readonly", width=12,
                     values=["title", "year", "rating", "hours", "genre", "status"],
                     style="Dark.TCombobox").pack(side="left")
        self.sort_var.trace("w", lambda *a: self.load_data())

        # Основная область
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        left = tk.Frame(main, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True)

        tree_frame = tk.Frame(left, bg=COLORS["border"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("id", "title", "studio", "genre", "platform", "year",
                "rating", "hours", "status", "progress")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", style="Dark.Treeview")
        widths = {"id": 45, "title": 220, "studio": 150, "genre": 110,
                  "platform": 70, "year": 65, "rating": 65, "hours": 70,
                  "status": 110, "progress": 85}
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=widths.get(c, 100),
                             anchor="center" if c not in ("title", "studio") else "w")
        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)

        sb = ttk.Scrollbar(tree_frame, orient="vertical",
                           command=self.tree.yview, style="Dark.Vertical.TScrollbar")
        sb.pack(side="right", fill="y", padx=(0, 1), pady=1)
        self.tree.configure(yscrollcommand=sb.set)

        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(status, foreground=color)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.open_fullscreen())

        # Превью
        right = tk.Frame(main, bg=COLORS["bg"], width=280)
        right.pack(side="right", fill="y", padx=(15, 0))
        right.pack_propagate(False)

        preview_card = tk.Frame(right, bg=COLORS["bg2"],
                                highlightthickness=1,
                                highlightbackground=COLORS["border"])
        preview_card.pack(fill="both", expand=True)

        tk.Label(preview_card, text="ПРЕВЬЮ", bg=COLORS["bg2"],
                 fg=COLORS["accent"], font=("Segoe UI", 10, "bold")
                 ).pack(pady=(12, 5))

        self.preview = tk.Label(preview_card, text="Нет обложки",
                                bg=COLORS["bg3"], fg=COLORS["fg_dim"],
                                font=("Segoe UI", 10),
                                width=30, height=16)
        self.preview.pack(padx=12, pady=12, fill="both", expand=True)

        # Форма
        form_card = tk.Frame(self.root, bg=COLORS["bg2"],
                             highlightthickness=1,
                             highlightbackground=COLORS["border"])
        form_card.pack(fill="x", padx=20, pady=(0, 10))

        form_inner = tk.Frame(form_card, bg=COLORS["bg2"])
        form_inner.pack(fill="x", padx=15, pady=12)

        tk.Label(form_inner, text="РЕДАКТИРОВАНИЕ", bg=COLORS["bg2"],
                 fg=COLORS["accent"], font=("Segoe UI", 10, "bold")
                 ).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        self.entries = {}
        row1 = ["title", "studio", "genre", "platform", "year"]
        row2 = ["rating", "hours", "status", "progress"]
        labels1 = {"title": "Название", "studio": "Студия", "genre": "Жанр",
                   "platform": "Платформа", "year": "Год"}
        labels2 = {"rating": "Рейтинг", "hours": "Часы",
                   "status": "Статус", "progress": "Прогресс %"}

        for i, f in enumerate(row1):
            tk.Label(form_inner, text=labels1[f], bg=COLORS["bg2"],
                     fg=COLORS["fg_dim"], font=("Segoe UI", 9)
                     ).grid(row=1, column=i, sticky="w", padx=3)
            e = tk.Entry(form_inner, width=18, bg=COLORS["bg3"],
                         fg=COLORS["fg"], insertbackground=COLORS["fg"],
                         relief="flat", font=("Segoe UI", 10),
                         highlightthickness=1,
                         highlightbackground=COLORS["border"],
                         highlightcolor=COLORS["accent"])
            e.grid(row=2, column=i, padx=3, pady=(0, 8), ipady=5, sticky="ew")
            self.entries[f] = e

        for i, f in enumerate(row2):
            tk.Label(form_inner, text=labels2[f], bg=COLORS["bg2"],
                     fg=COLORS["fg_dim"], font=("Segoe UI", 9)
                     ).grid(row=3, column=i, sticky="w", padx=3)
            if f == "status":
                cb = ttk.Combobox(form_inner, width=16, values=STATUSES,
                                  state="readonly", style="Dark.TCombobox")
                cb.grid(row=4, column=i, padx=3, pady=(0, 5), sticky="ew")
                self.entries[f] = cb
            else:
                e = tk.Entry(form_inner, width=18, bg=COLORS["bg3"],
                             fg=COLORS["fg"], insertbackground=COLORS["fg"],
                             relief="flat", font=("Segoe UI", 10),
                             highlightthickness=1,
                             highlightbackground=COLORS["border"],
                             highlightcolor=COLORS["accent"])
                e.grid(row=4, column=i, padx=3, pady=(0, 5), ipady=5, sticky="ew")
                self.entries[f] = e

        cover_frame = tk.Frame(form_inner, bg=COLORS["bg2"])
        cover_frame.grid(row=2, column=5, rowspan=3, padx=(15, 0), sticky="w")
        self.make_button(cover_frame, "📁 Файл", self.choose_cover).pack()
        self.cover_path_var = tk.StringVar()
        tk.Label(cover_frame, textvariable=self.cover_path_var,
                 bg=COLORS["bg2"], fg=COLORS["fg_dim"],
                 font=("Segoe UI", 8), wraplength=160
                 ).pack(pady=(5, 0), anchor="w")

        # Кнопки
        btns = tk.Frame(self.root, bg=COLORS["bg"])
        btns.pack(fill="x", padx=20, pady=(0, 12))

        self.make_button(btns, "➕  Добавить", self.add,
                         color=COLORS["success"]).pack(side="left", padx=(0, 8))
        self.make_button(btns, "✏️  Обновить", self.update,
                         color=COLORS["accent"]).pack(side="left", padx=(0, 8))
        self.make_button(btns, "🗑  Удалить", self.delete,
                         color=COLORS["danger"]).pack(side="left", padx=(0, 8))
        self.make_button(btns, "🖼  Открыть", self.open_fullscreen,
                         color=COLORS["accent2"]).pack(side="left", padx=(0, 8))

        self.make_button(btns, "📊  Статистика", self.show_stats,
                         color=COLORS["accent"]).pack(side="right", padx=(8, 0))
        self.make_button(btns, "⭐  Wishlist", self.show_wishlist,
                         color=COLORS["warning"]).pack(side="right", padx=(8, 0))

        # Статус-бар
        self.statusbar = tk.Label(self.root, text="Готово",
                                  bg=COLORS["bg2"], fg=COLORS["fg_dim"],
                                  font=("Segoe UI", 9), anchor="w",
                                  padx=15, pady=5)
        self.statusbar.pack(fill="x", side="bottom")

    # ---------- Логика ----------
    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        status_filter = self.status_var.get()
        if status_filter in ("Все", "", None):
            status_filter = None

        genre_filter = self.genre_var.get()
        if genre_filter in ("Все", "", None):
            genre_filter = None

        rows = db.get_games(self.sort_var.get(),
                            self.search_var.get(),
                            status_filter,
                            genre_filter)

        for g in rows:
            tag = g[8] if g[8] in STATUS_COLORS else ""
            self.tree.insert("", "end", tags=(tag,),
                values=(g[0], g[1], g[2], g[3], g[4], g[5], g[6],
                        g[7], g[8], f"{g[9]}%"))

        self.statusbar.config(text=f"Всего игр: {len(rows)}")

    def refresh_genres(self):
        self.genre_combo["values"] = ["Все"] + db.get_all_genres()
        self.genre_var.set("Все")

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_id = v[0]

        fields = ["title", "studio", "genre", "platform", "year",
                  "rating", "hours", "status"]
        for k, i in zip(fields, range(1, 9)):
            widget = self.entries[k]
            if isinstance(widget, ttk.Combobox):
                widget.set(v[i])
            else:
                widget.delete(0, tk.END)
                widget.insert(0, v[i])

        self.entries["progress"].delete(0, tk.END)
        self.entries["progress"].insert(0, str(v[9]).replace("%", ""))

        game = db.get_game(self.selected_id)
        if game:
            cover = game[10]
            self.cover_path_var.set(os.path.basename(cover) if cover else "")
            self.show_preview(cover)

    def show_preview(self, path):
        """Показывает превью. Если путь в БД пустой — ищет файл в images/."""
        if path and os.path.exists(path):
            self._load_preview(path)
            return

        if self.selected_id:
            game = db.get_game(self.selected_id)
            if game:
                title = game[1]
                safe = "".join(c for c in title if c.isalnum() or c in " -_").strip()
                candidates = [
                    os.path.join("images", safe + ".jpg"),
                    os.path.join("images", safe + ".png"),
                    os.path.join("images", title + ".jpg"),
                    os.path.join("images", title + ".png"),
                ]
                for c in candidates:
                    if os.path.exists(c):
                        conn = db.get_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE games SET cover_path=%s WHERE id=%s",
                                    (c, self.selected_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        self._load_preview(c)
                        return

        self.preview.config(image="", text="Нет обложки")
        self.preview_img = None

    def _load_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((250, 340))
            self.preview_img = ImageTk.PhotoImage(img)
            self.preview.config(image=self.preview_img, text="")
        except Exception as e:
            self.preview.config(image="", text=f"Ошибка: {e}")

    def choose_cover(self):
        p = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if p:
            os.makedirs("images", exist_ok=True)
            dst = os.path.join("images", os.path.basename(p))
            shutil.copy(p, dst)
            self.cover_path_var.set(os.path.basename(dst))

            if self.selected_id:
                game = db.get_game(self.selected_id)
                if game:
                    db.update_game(self.selected_id,
                                   game[1], game[2], game[3], game[4],
                                   game[5], game[6], game[7], game[8], game[9],
                                   dst)

            self.show_preview(dst)

    # ---------- CRUD ----------
    def _form(self):
        t = self.entries["title"].get().strip()
        if not t:
            messagebox.showerror("Ошибка", "Название обязательно")
            return None
        try:
            year = int(self.entries["year"].get() or 0)
            rating = float(self.entries["rating"].get() or 0)
            hours = float(self.entries["hours"].get() or 0)
            progress = int(self.entries["progress"].get() or 0)
        except ValueError:
            messagebox.showerror("Ошибка", "Год, рейтинг, часы и прогресс — числа")
            return None
        return (t,
                self.entries["studio"].get().strip(),
                self.entries["genre"].get().strip(),
                self.entries["platform"].get().strip(),
                year, rating, hours,
                self.entries["status"].get().strip(),
                progress)

    def add(self):
        d = self._form()
        if d:
            cover = ""
            safe = "".join(c for c in d[0] if c.isalnum() or c in " -_").strip()
            for ext in (".jpg", ".png", ".jpeg"):
                candidate = os.path.join("images", safe + ext)
                if os.path.exists(candidate):
                    cover = candidate
                    break

            db.add_game(*d, cover)
            self.load_data()
            self.refresh_genres()
            self.clear_form()
            self.statusbar.config(text="✅ Игра добавлена")

    def update(self):
        if not self.selected_id:
            return messagebox.showwarning("Внимание", "Выберите игру")
        d = self._form()
        if d:
            game = db.get_game(self.selected_id)
            cover = game[10] if game else ""
            db.update_game(self.selected_id, *d, cover)
            self.load_data()
            self.refresh_genres()
            self.statusbar.config(text="✏️ Запись обновлена")

    def delete(self):
        if not self.selected_id:
            return
        if messagebox.askyesno("Удалить?", "Удалить эту игру?"):
            db.delete_game(self.selected_id)
            self.load_data()
            self.refresh_genres()
            self.clear_form()
            self.preview.config(image="", text="Нет обложки")
            self.statusbar.config(text="🗑 Игра удалена")

    def clear_form(self):
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, tk.END)
        self.cover_path_var.set("")
        self.selected_id = None

    # ---------- Просмотр ----------
    def open_fullscreen(self):
        if not self.selected_id:
            return
        game = db.get_game(self.selected_id)
        if not game:
            return

        path = game[10]
        if not path or not os.path.exists(path):
            safe = "".join(c for c in game[1] if c.isalnum() or c in " -_").strip()
            for ext in (".jpg", ".png", ".jpeg"):
                candidate = os.path.join("images", safe + ext)
                if os.path.exists(candidate):
                    path = candidate
                    break

        if not path or not os.path.exists(path):
            return messagebox.showinfo("Нет обложки",
                                       "У этой игры нет файла обложки.\n"
                                       "Нажми '📁 Файл', чтобы выбрать вручную.")

        win = tk.Toplevel(self.root)
        win.title(game[1])
        win.configure(bg=COLORS["bg"])
        img = Image.open(path)
        img.thumbnail((900, 700))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(win, image=photo, bg=COLORS["bg"])
        lbl.image = photo
        lbl.pack(padx=20, pady=(20, 5))
        tk.Label(win, text=game[1], bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))

    # ---------- Статистика ----------
    def show_stats(self):
        total, by_status, by_genre, top_hours = db.get_stats()

        win = tk.Toplevel(self.root)
        win.title("📊 Статистика")
        win.geometry("500x560")
        win.configure(bg=COLORS["bg"])

        tk.Label(win, text="📊  СТАТИСТИКА КОЛЛЕКЦИИ",
                 bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(pady=15)

        cards = tk.Frame(win, bg=COLORS["bg"])
        cards.pack(pady=10)
        for i, (label, value, color) in enumerate([
            ("Всего игр", str(total[0]), COLORS["accent"]),
            ("Часов", f"{total[1] or 0:.0f}", COLORS["success"]),
            ("Ср. рейтинг", f"{total[2] or 0:.2f}", COLORS["warning"]),
        ]):
            card = tk.Frame(cards, bg=COLORS["bg2"],
                            highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.grid(row=0, column=i, padx=8)
            tk.Label(card, text=str(value), bg=COLORS["bg2"], fg=color,
                     font=("Segoe UI", 20, "bold")).pack(padx=20, pady=(12, 0))
            tk.Label(card, text=label, bg=COLORS["bg2"], fg=COLORS["fg_dim"],
                     font=("Segoe UI", 9)).pack(padx=20, pady=(0, 12))

        text = tk.Text(win, bg=COLORS["bg2"], fg=COLORS["fg"],
                       font=("Segoe UI", 10), relief="flat",
                       padx=15, pady=15, wrap="word",
                       highlightthickness=1,
                       highlightbackground=COLORS["border"])
        text.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        text.tag_configure("head", foreground=COLORS["accent"],
                          font=("Segoe UI", 11, "bold"))
        text.tag_configure("item", foreground=COLORS["fg"])

        text.insert("end", "📁  По статусам\n", "head")
        for s, c in by_status:
            text.insert("end", f"    • {s or '—'}: {c}\n", "item")
        text.insert("end", "\n🎯  По жанрам\n", "head")
        for g, c in by_genre:
            text.insert("end", f"    • {g or '—'}: {c}\n", "item")
        text.insert("end", "\n🏆  Топ-5 по часам\n", "head")
        for i, (t, h) in enumerate(top_hours, 1):
            text.insert("end", f"    {i}. {t} — {h or 0:.1f} ч\n", "item")
        text.config(state="disabled")

    # ---------- Wishlist ----------
    def show_wishlist(self):
        rows = db.get_wishlist()
        win = tk.Toplevel(self.root)
        win.title("⭐ Wishlist")
        win.geometry("600x450")
        win.configure(bg=COLORS["bg"])

        tk.Label(win, text="⭐  ХОЧУ КУПИТЬ",
                 bg=COLORS["bg"], fg=COLORS["warning"],
                 font=("Segoe UI", 14, "bold")).pack(pady=15)

        if not rows:
            tk.Label(win, text="Список пуст", bg=COLORS["bg"],
                     fg=COLORS["fg_dim"], font=("Segoe UI", 11)).pack(pady=50)
            return

        frame = tk.Frame(win, bg=COLORS["bg2"], highlightthickness=1,
                         highlightbackground=COLORS["border"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for i, g in enumerate(rows, 1):
            row = tk.Frame(frame, bg=COLORS["bg2"])
            row.pack(fill="x", padx=15, pady=8)
            tk.Label(row, text=f"{i}.", bg=COLORS["bg2"], fg=COLORS["accent"],
                     font=("Segoe UI", 12, "bold"), width=3).pack(side="left")
            info = tk.Frame(row, bg=COLORS["bg2"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=g[1], bg=COLORS["bg2"], fg=COLORS["fg"],
                     font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x")
            tk.Label(info, text=f"{g[5]} • {g[4]} • {g[3]} • {g[2]}",
                     bg=COLORS["bg2"], fg=COLORS["fg_dim"],
                     font=("Segoe UI", 9), anchor="w").pack(fill="x")


if __name__ == "__main__":
    root = tk.Tk()
    app = GameVaultApp(root)
    root.mainloop()