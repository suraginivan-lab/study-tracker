import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import database as db


class TagsDialog:
    def __init__(self, parent):
        self.parent = parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Управление тегами")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.load_tags()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть - список тегов
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(left_frame, text="Теги:", font=(
            'Arial', 10, 'bold')).pack(anchor=tk.W)

        columns = ('id', 'name', 'color')
        self.tree = ttk.Treeview(
            left_frame, columns=columns, show='headings', height=15)

        self.tree.column('id', width=50)
        self.tree.column('name', width=150)
        self.tree.column('color', width=100)

        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('color', text='Цвет')

        vsb = ttk.Scrollbar(left_frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Правая часть - кнопки
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Button(right_frame, text="➕ Добавить",
                   command=self.add_tag, width=20).pack(pady=2)
        ttk.Button(right_frame, text="✏️ Редактировать",
                   command=self.edit_tag, width=20).pack(pady=2)
        ttk.Button(right_frame, text="🗑️ Удалить",
                   command=self.delete_tag, width=20).pack(pady=2)
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Закрыть",
                   command=self.dialog.destroy, width=20).pack(pady=2)

    def load_tags(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tags = db.get_all_tags()
        for tag in tags:
            self.tree.insert('', tk.END, values=(tag[0], tag[1], tag[2]))

    def add_tag(self):
        dialog = TagEditDialog(self.dialog)
        self.dialog.wait_window(dialog)
        self.load_tags()

    def edit_tag(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Предупреждение", "Выберите тег для редактирования")
            return

        tag_id = self.tree.item(selected[0])['values'][0]
        dialog = TagEditDialog(self.dialog, tag_id)
        self.dialog.wait_window(dialog)
        self.load_tags()

    def delete_tag(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Предупреждение", "Выберите тег для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот тег?"):
            tag_id = self.tree.item(selected[0])['values'][0]
            db.delete_tag(tag_id)
            self.load_tags()


class TagEditDialog:
    def __init__(self, parent, tag_id=None):
        self.parent = parent
        self.tag_id = tag_id

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(
            "Добавление тега" if not tag_id else "Редактирование тега")
        self.dialog.geometry("350x180")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.name_var = tk.StringVar()
        self.color_var = tk.StringVar(value="#2ecc71")

        if tag_id:
            self.load_tag()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Название *").grid(row=0,
                                                      column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.name_var,
                  width=25).grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Цвет").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        self.color_btn = tk.Button(color_frame, bg=self.color_var.get(),
                                   width=3, command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

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

    def load_tag(self):
        tags = db.get_all_tags()
        for tag in tags:
            if tag[0] == self.tag_id:
                self.name_var.set(tag[1])
                self.color_var.set(tag[2])
                self.color_btn.config(bg=tag[2])
                break

    def save(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Ошибка", "Название обязательно")
            return

        try:
            if self.tag_id:
                db.update_tag(
                    self.tag_id,
                    self.name_var.get().strip(),
                    self.color_var.get()
                )
            else:
                db.add_tag(
                    self.name_var.get().strip(),
                    self.color_var.get()
                )

            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
