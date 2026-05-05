import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Book Tracker")
        self.geometry("850x600")
        self.resizable(True, True)
        self.books = []
        self.setup_ui()

    def setup_ui(self):
        # --- Форма ввода ---
        input_frame = ttk.LabelFrame(self, text="Добавить книгу")
        input_frame.pack(pady=10, padx=10, fill="x")

        fields = [
            ("Название книги:", "title"),
            ("Автор:", "author"),
            ("Жанр:", "genre"),
            ("Количество страниц:", "pages")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            self.entries[key] = ttk.Entry(input_frame, width=50)
            self.entries[key].grid(row=i, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(input_frame, text="➕ Добавить книгу", command=self.add_book).grid(
            row=len(fields), column=0, columnspan=2, pady=10, sticky="ew"
        )

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(self, text="Фильтрация")
        filter_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5)
        self.genre_filter = ttk.Entry(filter_frame, width=15)
        self.genre_filter.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Страницы больше:").grid(row=0, column=2, padx=5)
        self.pages_filter = ttk.Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="🔍 Применить", command=self.apply_filter).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="🔄 Сбросить", command=self.reset_filter).grid(row=0, column=5, padx=5)

        # --- Таблица ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("title", "author", "genre", "pages"), show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страницы")

        self.tree.column("title", width=250)
        self.tree.column("author", width=180)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # --- Кнопки сохранения/загрузки ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5, padx=10, fill="x")
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_json).pack(side="left", padx=5)

    def validate_and_get_data(self):
        title = self.entries["title"].get().strip()
        author = self.entries["author"].get().strip()
        genre = self.entries["genre"].get().strip()
        pages_str = self.entries["pages"].get().strip()

        if not all([title, author, genre, pages_str]):
            messagebox.showerror("Ошибка ввода", "Все поля должны быть заполнены!")
            return None

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество страниц должно быть целым положительным числом!")
            return None

        return {"title": title, "author": author, "genre": genre, "pages": pages}

    def add_book(self):
        book = self.validate_and_get_data()
        if not book:
            return
        self.books.append(book)
        self.refresh_table(self.books)
        self.clear_entries()
        messagebox.showinfo("Успех", "Книга успешно добавлена!")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def refresh_table(self, books_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in books_list:
            self.tree.insert("", "end", values=(b["title"], b["author"], b["genre"], b["pages"]))

    def apply_filter(self):
        genre_f = self.genre_filter.get().strip().lower()
        pages_f_str = self.pages_filter.get().strip()

        filtered = self.books
        if genre_f:
            filtered = [b for b in filtered if b["genre"].lower() == genre_f]
        if pages_f_str:
            try:
                pages_val = int(pages_f_str)
                filtered = [b for b in filtered if b["pages"] > pages_val]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Значение для страниц должно быть числом!")
                return
        self.refresh_table(filtered)

    def reset_filter(self):
        self.genre_filter.delete(0, tk.END)
        self.pages_filter.delete(0, tk.END)
        self.refresh_table(self.books)

    def save_json(self, filename="books.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_json(self, filename="books.json"):
        if not os.path.exists(filename):
            messagebox.showwarning("Файл не найден", f"{filename} отсутствует в папке с программой.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.refresh_table(self.books)
            messagebox.showinfo("Успех", f"Данные загружены из {filename}")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл повреждён или имеет неверный формат JSON.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    app = BookTrackerApp()
    app.mainloop()