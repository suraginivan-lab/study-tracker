import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

class AddEditDialog:
    def __init__(self, parent, callback, item_id=None):
        self.parent = parent
        self.callback = callback
        self.item_id = item_id
        self.result = None
        
        # Создаем окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавление записи" if not item_id else "Редактирование записи")
        self.dialog.geometry("650x750")
        
        # Устанавливаем связь с родителем
        self.dialog.transient(parent)
        
        # Переменные
        self.title_var = tk.StringVar()
        self.description_text = None
        self.category_var = tk.StringVar()
        self.rating_var = tk.IntVar(value=3)
        self.status_var = tk.StringVar(value="planned")
        
        # Устанавливаем дедлайн на 7 дней вперед
        default_deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.deadline_var = tk.StringVar(value=default_deadline)
        self.hours_var = tk.DoubleVar(value=0)
        self.priority_var = tk.IntVar(value=3)
        
        # Для тегов
        self.tag_vars = {}
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Загружаем данные если редактирование
        if item_id:
            self.load_item_data()
        
        # Центрируем окно после создания
        self.dialog.after(10, self.center_window)
        
        # Делаем окно модальным после его отображения
        self.dialog.after(20, self.make_modal)
        
        # Обрабатываем закрытие окна
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def center_window(self):
        """Центрирование окна относительно родителя"""
        try:
            self.dialog.update_idletasks()
            
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            self.dialog.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Ошибка центрирования: {e}")
        
    def make_modal(self):
        """Делаем окно модальным"""
        try:
            # Проверяем, что окно отображается
            if self.dialog.winfo_viewable():
                self.dialog.grab_set()
                self.dialog.focus_set()
                print("Окно стало модальным")
            else:
                # Если окно еще не отображается, пробуем снова
                self.dialog.after(50, self.make_modal)
        except Exception as e:
            print(f"Ошибка при установке модальности: {e}")
            # Пробуем еще раз
            self.dialog.after(50, self.make_modal)
    
    def on_close(self):
        """Обработка закрытия окна"""
        try:
            self.dialog.grab_release()
        except:
            pass
        self.dialog.destroy()
        
    def setup_ui(self):
        """Создание интерфейса диалога"""
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем холст с прокруткой
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контейнер для полей
        fields_frame = ttk.Frame(scrollable_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Название
        self.create_label(fields_frame, "Название *", 0)
        title_entry = ttk.Entry(fields_frame, textvariable=self.title_var, width=60, font=('Arial', 10))
        title_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        # Описание
        self.create_label(fields_frame, "Описание", 1)
        
        description_frame = ttk.Frame(fields_frame)
        description_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        self.description_text = tk.Text(description_frame, width=60, height=5, 
                                       wrap=tk.WORD, font=('Arial', 10))
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        desc_scrollbar = ttk.Scrollbar(description_frame, orient=tk.VERTICAL, 
                                       command=self.description_text.yview)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        
        # Категория
        self.create_label(fields_frame, "Категория", 2)
        
        categories = db.get_all_categories()
        category_list = [cat[1] for cat in categories]
        
        if category_list:
            self.category_combo = ttk.Combobox(fields_frame, textvariable=self.category_var, 
                                              values=category_list, state='readonly', 
                                              width=57, font=('Arial', 10))
            self.category_combo.grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=5)
            
            # Выбираем категорию по умолчанию
            default_selected = False
            for cat in categories:
                if len(cat) > 4 and cat[4]:  # is_default
                    self.category_var.set(cat[1])
                    default_selected = True
                    break
            if not default_selected and categories:
                self.category_var.set(categories[0][1])
        
        # Статус
        self.create_label(fields_frame, "Статус", 3)
        
        status_frame = ttk.Frame(fields_frame)
        status_frame.grid(row=3, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        statuses = [
            ('📅 Запланировано', 'planned'),
            ('⚡ В процессе', 'in_progress'),
            ('✅ Завершено', 'completed'),
            ('⏸ На паузе', 'on_hold')
        ]
        
        for i, (text, value) in enumerate(statuses):
            rb = ttk.Radiobutton(status_frame, text=text, variable=self.status_var, 
                                value=value)
            rb.grid(row=0, column=i, padx=(0, 15))
        
        # Приоритет
        self.create_label(fields_frame, "Приоритет", 4)
        
        priority_frame = ttk.Frame(fields_frame)
        priority_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        for i in range(1, 6):
            rb = ttk.Radiobutton(priority_frame, text=f"{'⚡' * i} ({i})", 
                                variable=self.priority_var, value=i)
            rb.grid(row=0, column=i-1, padx=(0, 10))
        
        # Рейтинг
        self.create_label(fields_frame, "Рейтинг", 5)
        
        rating_frame = ttk.Frame(fields_frame)
        rating_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        for i in range(1, 6):
            rb = ttk.Radiobutton(rating_frame, text="★" * i, 
                                variable=self.rating_var, value=i)
            rb.grid(row=0, column=i-1, padx=(0, 10))
        
        # Дедлайн
        self.create_label(fields_frame, "Дедлайн", 6)
        
        deadline_frame = ttk.Frame(fields_frame)
        deadline_frame.grid(row=6, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        deadline_entry = ttk.Entry(deadline_frame, textvariable=self.deadline_var, 
                                  width=20, font=('Arial', 10))
        deadline_entry.pack(side=tk.LEFT)
        
        ttk.Label(deadline_frame, text=" (ГГГГ-ММ-ДД)", font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Кнопка "Сегодня"
        ttk.Button(deadline_frame, text="Сегодня", 
                  command=self.set_today_deadline).pack(side=tk.LEFT, padx=(10, 0))
        
        # Затрачено часов
        self.create_label(fields_frame, "Часов затрачено", 7)
        
        hours_frame = ttk.Frame(fields_frame)
        hours_frame.grid(row=7, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        hours_entry = ttk.Entry(hours_frame, textvariable=self.hours_var, 
                               width=10, font=('Arial', 10))
        hours_entry.pack(side=tk.LEFT)
        ttk.Label(hours_frame, text=" ч", font=('Arial', 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Теги
        self.create_label(fields_frame, "Теги", 8)
        
        # Создаем фрейм с прокруткой для тегов
        tags_container = ttk.LabelFrame(fields_frame, text="Выберите теги")
        tags_container.grid(row=8, column=1, columnspan=3, sticky=tk.W+tk.E, pady=5, padx=5)
        
        tags_canvas = tk.Canvas(tags_container, height=120, highlightthickness=0)
        tags_scrollbar = ttk.Scrollbar(tags_container, orient="vertical", command=tags_canvas.yview)
        tags_frame = ttk.Frame(tags_canvas)
        
        tags_frame.bind(
            "<Configure>",
            lambda e: tags_canvas.configure(scrollregion=tags_canvas.bbox("all"))
        )
        
        tags_canvas.create_window((0, 0), window=tags_frame, anchor="nw")
        tags_canvas.configure(yscrollcommand=tags_scrollbar.set)
        
        tags_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tags_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Загружаем теги
        tags = db.get_all_tags()
        for i, tag in enumerate(tags):
            var = tk.BooleanVar()
            self.tag_vars[tag[0]] = var
            cb = ttk.Checkbutton(tags_frame, text=tag[1], variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=15, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=9, column=0, columnspan=4, pady=(30, 10))
        
        save_btn = ttk.Button(button_frame, text="💾 Сохранить", command=self.save, 
                             width=15, style='Accent.TButton')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(button_frame, text="❌ Отмена", command=self.on_close, 
                               width=15)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Настройка стиля для акцентной кнопки
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Настройка весов колонок
        fields_frame.columnconfigure(1, weight=1)
        
    def create_label(self, parent, text, row):
        """Создание метки"""
        label = ttk.Label(parent, text=text, font=('Arial', 10, 'bold'))
        label.grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        return label
    
    def set_today_deadline(self):
        """Установка дедлайна на сегодня"""
        self.deadline_var.set(datetime.now().strftime("%Y-%m-%d"))
        
    def load_item_data(self):
        """Загрузка данных для редактирования"""
        result = db.get_study_item_by_id(self.item_id)
        if result:
            item, tags = result
        else:
            item, tags = None, []
        
        if item:
            self.title_var.set(item[1] if item[1] else "")
            
            if self.description_text and len(item) > 2 and item[2]:
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert('1.0', item[2])
            
            # Получаем название категории
            if len(item) > 3 and item[3]:
                categories = db.get_all_categories()
                for cat in categories:
                    if cat[0] == item[3]:
                        self.category_var.set(cat[1])
                        break
            
            if len(item) > 4 and item[4]:
                self.rating_var.set(item[4])
            if len(item) > 5 and item[5]:
                self.status_var.set(item[5])
            if len(item) > 7 and item[7]:
                self.deadline_var.set(item[7])
            if len(item) > 8 and item[8]:
                self.hours_var.set(item[8])
            if len(item) > 9 and item[9]:
                self.priority_var.set(item[9])
            
            # Отмечаем теги
            if tags:
                for tag in tags:
                    if len(tag) > 0 and tag[0] in self.tag_vars:
                        self.tag_vars[tag[0]].set(True)
    
    def save(self):
        """Сохранение записи"""
        # Валидация
        if not self.title_var.get().strip():
            messagebox.showerror("Ошибка", "Название обязательно для заполнения", 
                               parent=self.dialog)
            return
        
        # Получаем ID категории
        category_id = None
        category_name = self.category_var.get()
        if category_name:
            categories = db.get_all_categories()
            for cat in categories:
                if cat[1] == category_name:
                    category_id = cat[0]
                    break
        
        # Получаем выбранные теги
        selected_tags = [tag_id for tag_id, var in self.tag_vars.items() if var.get()]
        
        # Получаем текст описания
        description = ""
        if self.description_text:
            description = self.description_text.get('1.0', tk.END).strip()
        
        # Проверка формата даты
        deadline = self.deadline_var.get().strip()
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД", 
                                   parent=self.dialog)
                return
        
        # Собираем данные
        data = {
            'title': self.title_var.get().strip(),
            'description': description,
            'category_id': category_id,
            'rating': self.rating_var.get(),
            'status': self.status_var.get(),
            'deadline': deadline if deadline else None,
            'hours_spent': self.hours_var.get(),
            'priority': self.priority_var.get(),
            'tags': selected_tags
        }
        
        try:
            if self.item_id:
                db.update_study_item(self.item_id, data)
                messagebox.showinfo("Успех", "Запись успешно обновлена", parent=self.dialog)
            else:
                db.add_study_item(data)
                messagebox.showinfo("Успех", "Запись успешно добавлена", parent=self.dialog)
            
            if self.callback:
                self.callback()
            self.on_close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись:\n{str(e)}", 
                               parent=self.dialog)