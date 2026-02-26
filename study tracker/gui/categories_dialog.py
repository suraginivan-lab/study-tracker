import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import database as db


class CategoriesDialog:
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Управление категориями")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть - список категорий
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(left_frame, text="Категории:", font=(
            'Arial', 10, 'bold')).pack(anchor=tk.W)

        # Таблица категорий
        columns = ('id', 'name', 'description', 'color', 'default')
        self.tree = ttk.Treeview(
            left_frame, columns=columns, show='headings', height=15)

        self.tree.column('id', width=50)
        self.tree.column('name', width=150)
        self.tree.column('description', width=200)
        self.tree.column('color', width=50)
        self.tree.column('default', width=70)

        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('description', text='Описание')
        self.tree.heading('color', text='Цвет')
        self.tree.heading('default', text='По умолч.')

        vsb = ttk.Scrollbar(left_frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Правая часть - кнопки управления
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Button(right_frame, text="➕ Добавить",
                   command=self.add_category, width=20).pack(pady=2)
        ttk.Button(right_frame, text="✏️ Редактировать",
                   command=self.edit_category, width=20).pack(pady=2)
        ttk.Button(right_frame, text="🗑️ Удалить",
                   command=self.delete_category, width=20).pack(pady=2)
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Закрыть",
                   command=self.dialog.destroy, width=20).pack(pady=2)

    def load_categories(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        categories = db.get_all_categories()
        for cat in categories:
            self.tree.insert('', tk.END, values=(
                cat[0], cat[1], cat[2], cat[3],
                "✓" if cat[4] else ""
            ))

    def on_select(self, event):
        pass

    def add_category(self):
        dialog = CategoryEditDialog(self.dialog)
        self.dialog.wait_window(dialog)
        self.load_categories()
        if self.callback:
            self.callback()

    def edit_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Предупреждение", "Выберите категорию для редактирования")
            return

        category_id = self.tree.item(selected[0])['values'][0]
        dialog = CategoryEditDialog(self.dialog, category_id)
        self.dialog.wait_window(dialog)
        self.load_categories()
        if self.callback:
            self.callback()

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Предупреждение", "Выберите категорию для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту категорию?"):
            category_id = self.tree.item(selected[0])['values'][0]
            db.delete_category(category_id)
            self.load_categories()
            if self.callback:
                self.callback()


class CategoryEditDialog:
    def __init__(self, parent, category_id=None):
        self.parent = parent
        self.category_id = category_id

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(
            "Добавление категории" if not category_id else "Редактирование категории")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.color_var = tk.StringVar(value="#3498db")
        self.default_var = tk.BooleanVar()

        if category_id:
            self.load_category()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Название
        ttk.Label(main_frame, text="Название *").grid(row=0,
                                                      column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.name_var,
                  width=30).grid(row=0, column=1, pady=5)

        # Описание
        ttk.Label(main_frame, text="Описание").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.description_var,
                  width=30).grid(row=1, column=1, pady=5)

        # Цвет
        ttk.Label(main_frame, text="Цвет").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        self.color_btn = tk.Button(color_frame, bg=self.color_var.get(),
                                   width=3, command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT)

        # По умолчанию
        ttk.Checkbutton(main_frame, text="Категория по умолчанию",
                        variable=self.default_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить",
                   command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def choose_color(self):
        color = colorchooser.askcolor(
            color=self.color_var.get(), title="Выберите цвет")
        if color[1]:
            self.color_var.set(color[1])
            self.color_btn.config(bg=color[1])

    def load_category(self):
        categories = db.get_all_categories()
        for cat in categories:
            if cat[0] == self.category_id:
                self.name_var.set(cat[1])
                self.description_var.set(cat[2])
                self.color_var.set(cat[3])
                self.default_var.set(cat[4])
                self.color_btn.config(bg=cat[3])
                break

    def save(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Ошибка", "Название обязательно")
            return

        try:
            if self.category_id:
                db.update_category(
                    self.category_id,
                    self.name_var.get().strip(),
                    self.description_var.get().strip(),
                    self.color_var.get(),
                    self.default_var.get()
                )
            else:
                db.add_category(
                    self.name_var.get().strip(),
                    self.description_var.get().strip(),
                    self.color_var.get(),
                    self.default_var.get()
                )

            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
