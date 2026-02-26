import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from .add_edit_dialog import AddEditDialog
from .categories_dialog import CategoriesDialog
from .tags_dialog import TagsDialog
from datetime import datetime

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Трекер учебы - Управление учебными материалами")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.config(bg="#f5f5f5")
        
        # Переменные для поиска
        self.search_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="all")
        self.category_filter_var = tk.StringVar(value="all")
        
        # Контекстное меню (создаём один раз)
        self.context_menu = None
        self.create_context_menu()
        
        self.setup_menu()
        self.setup_toolbar()
        self.setup_search_panel()
        self.setup_main_area()
        self.setup_status_bar()
        
        # Загружаем данные
        self.load_data()
        
        # Обновляем статистику
        self.update_statistics()
        
        # Привязываем глобальное событие для скрытия меню
        self.root.bind('<Button-1>', self.hide_context_menu)
        
    def create_context_menu(self):
        """Создание контекстного меню (один раз)"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Редактировать", command=self.edit_item)
        self.context_menu.add_command(label="🗑️ Удалить", command=self.delete_item)
        self.context_menu.add_separator()
        
        # Подменю для изменения статуса
        status_menu = tk.Menu(self.context_menu, tearoff=0)
        status_menu.add_command(label="📅 Запланировано", 
                               command=lambda: self.change_status('planned'))
        status_menu.add_command(label="⚡ В процессе", 
                               command=lambda: self.change_status('in_progress'))
        status_menu.add_command(label="✅ Завершено", 
                               command=lambda: self.change_status('completed'))
        status_menu.add_command(label="⏸ На паузе", 
                               command=lambda: self.change_status('on_hold'))
        
        self.context_menu.add_cascade(label="📊 Изменить статус", menu=status_menu)
        
    def hide_context_menu(self, event):
        """Скрытие контекстного меню при клике вне его"""
        try:
            if self.context_menu:
                self.context_menu.unpost()
        except:
            pass
            
    def setup_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_command(label="Импорт данных", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Данные
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Данные", menu=data_menu)
        data_menu.add_command(label="Добавить", command=self.add_item)
        data_menu.add_command(label="Редактировать", command=self.edit_item)
        data_menu.add_command(label="Удалить", command=self.delete_item)
        data_menu.add_separator()
        data_menu.add_command(label="Управление категориями", command=self.manage_categories)
        data_menu.add_command(label="Управление тегами", command=self.manage_tags)
        
        # Меню Поиск
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Поиск", menu=search_menu)
        search_menu.add_command(label="Все записи", command=self.show_all)
        search_menu.add_command(label="В процессе", 
                               command=lambda: self.filter_by_status('in_progress'))
        search_menu.add_command(label="Запланированные", 
                               command=lambda: self.filter_by_status('planned'))
        search_menu.add_command(label="Завершенные", 
                               command=lambda: self.filter_by_status('completed'))
        
        # Меню Отчеты
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=reports_menu)
        reports_menu.add_command(label="Статистика", command=self.show_statistics)
        reports_menu.add_command(label="Прогресс по категориям", command=self.show_category_progress)
        
    def setup_toolbar(self):
        """Создание панели инструментов"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Кнопки
        ttk.Button(toolbar, text="➕ Добавить", command=self.add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Редактировать", command=self.edit_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Удалить", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        ttk.Button(toolbar, text="🔄 Обновить", command=self.load_data).pack(side=tk.LEFT, padx=2)
        
    def setup_search_panel(self):
        """Создание панели поиска"""
        search_frame = ttk.LabelFrame(self.root, text="Поиск и фильтрация", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поиск по тексту
        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        search_entry.bind('<Return>', lambda e: self.search())
        
        ttk.Button(search_frame, text="🔍 Найти", command=self.search).grid(row=0, column=2, padx=2)
        ttk.Button(search_frame, text="🔄 Сбросить", command=self.reset_filters).grid(row=0, column=3, padx=2)
        
        # Фильтры
        ttk.Label(search_frame, text="Статус:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var, 
                                    values=['all', 'planned', 'in_progress', 'completed', 'on_hold'],
                                    state='readonly', width=15)
        status_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.search())
        
        ttk.Label(search_frame, text="Категория:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_filter_var, 
                                          state='readonly', width=20)
        self.category_combo.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.update_category_filter()
        
    def setup_main_area(self):
        """Создание основной области с таблицей"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создаем таблицу
        columns = ('id', 'title', 'category', 'status', 'rating', 'deadline', 'hours', 'priority', 'tags')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('title', width=250, anchor=tk.W)
        self.tree.column('category', width=150, anchor=tk.W)
        self.tree.column('status', width=120, anchor=tk.CENTER)
        self.tree.column('rating', width=80, anchor=tk.CENTER)
        self.tree.column('deadline', width=100, anchor=tk.CENTER)
        self.tree.column('hours', width=80, anchor=tk.CENTER)
        self.tree.column('priority', width=80, anchor=tk.CENTER)
        self.tree.column('tags', width=200, anchor=tk.W)
        
        # Заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('status', text='Статус')
        self.tree.heading('rating', text='Рейтинг')
        self.tree.heading('deadline', text='Дедлайн')
        self.tree.heading('hours', text='Часов')
        self.tree.heading('priority', text='Приоритет')
        self.tree.heading('tags', text='Теги')
        
        # Добавляем скроллбары
        vsb = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Привязываем события
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_item())
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Button-1>', self.on_tree_click)  # Скрываем меню при клике на таблицу
        
        # Настройка цветов для статусов
        self.tree.tag_configure('completed', background='#e8f5e9')
        self.tree.tag_configure('in_progress', background='#fff3e0')
        self.tree.tag_configure('planned', background='#e3f2fd')
        self.tree.tag_configure('on_hold', background='#ffebee')
        self.tree.tag_configure('overdue', background='#ffcdd2')
        
    def on_tree_click(self, event):
        """Обработка клика по таблице - скрываем контекстное меню"""
        self.hide_context_menu(event)
        
    def setup_status_bar(self):
        """Создание статусной панели"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.stats_label = ttk.Label(self.status_bar, text="", relief=tk.SUNKEN, anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=5)
        
    def load_data(self):
        """Загрузка данных в таблицу"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Получаем данные
        items = db.get_all_study_items()
        
        # Заполняем таблицу
        current_date = datetime.now().date()
        
        for item in items:
            try:
                # Определяем статус просрочки
                deadline = item[7] if len(item) > 7 else None  # deadline
                status = item[5] if len(item) > 5 else ''     # status
                tags = item[11] if len(item) > 11 else ''
                
                # Форматируем данные
                title = item[1] if len(item) > 1 else ''
                category = item[9] if len(item) > 9 and item[9] else 'Без категории'
                status_text = self.get_status_text(status)
                
                # Рейтинг
                rating_val = item[4] if len(item) > 4 and item[4] else 0
                rating = '★' * rating_val if rating_val else '-'
                
                # Дедлайн
                deadline_str = item[7] if len(item) > 7 and item[7] else '-'
                
                # Часы
                hours = item[8] if len(item) > 8 and item[8] else 0
                hours_str = f"{hours} ч"
                
                # Приоритет
                priority_val = item[9] if len(item) > 9 and item[9] else 3
                priority = '⚡' * priority_val
                
                values = (
                    item[0],  # id
                    title,
                    category,
                    status_text,
                    rating,
                    deadline_str,
                    hours_str,
                    priority,
                    tags
                )
                
                # Определяем тег для цвета строки
                row_tags = []
                if deadline and deadline != '-' and status not in ['completed', 'on_hold']:
                    try:
                        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                        if deadline_date < current_date:
                            row_tags.append('overdue')
                        else:
                            row_tags.append(status)
                    except:
                        row_tags.append(status)
                else:
                    row_tags.append(status)
                
                self.tree.insert('', tk.END, values=values, tags=row_tags)
                
            except Exception as e:
                print(f"Ошибка при загрузке строки: {e}")
                continue
        
        self.update_status(f"Загружено записей: {len(items)}")
        
    def get_status_text(self, status):
        """Получение текстового представления статуса"""
        statuses = {
            'planned': '📅 Запланировано',
            'in_progress': '⚡ В процессе',
            'completed': '✅ Завершено',
            'on_hold': '⏸ На паузе'
        }
        return statuses.get(status, status)
    
    def update_status(self, message):
        """Обновление статусной строки"""
        self.status_label.config(text=message)
        
    def update_statistics(self):
        """Обновление статистики"""
        try:
            stats = db.get_statistics()
            self.stats_label.config(
                text=f"Всего: {stats['total']} | Завершено: {stats['by_status'].get('completed', 0)} | "
                     f"Часов: {stats['total_hours']} | Ср. рейтинг: {stats['avg_rating']:.1f}"
            )
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")
        
    def update_category_filter(self):
        """Обновление списка категорий в фильтре"""
        try:
            categories = db.get_all_categories()
            category_list = ['all'] + [cat[1] for cat in categories]
            self.category_combo['values'] = category_list
        except Exception as e:
            print(f"Ошибка при обновлении фильтра категорий: {e}")
        
    def add_item(self):
        """Добавление новой записи"""
        try:
            dialog = AddEditDialog(self.root, self.load_data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно добавления:\n{str(e)}")
        
    def edit_item(self):
        """Редактирование записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return
        
        try:
            # Получаем ID записи
            item_id = self.tree.item(selected[0])['values'][0]
            
            dialog = AddEditDialog(self.root, self.load_data, item_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно редактирования:\n{str(e)}")
        
    def delete_item(self):
        """Удаление записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            try:
                item_id = self.tree.item(selected[0])['values'][0]
                db.delete_study_item(item_id)
                self.load_data()
                self.update_statistics()
                self.update_status("Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить запись:\n{str(e)}")
            
    def search(self):
        """Поиск записей"""
        try:
            query = self.search_var.get()
            status = self.status_filter_var.get()
            category = self.category_filter_var.get()
            
            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Выполняем поиск
            items = db.search_study_items(
                query if query else None,
                status if status != 'all' else None,
                category if category != 'all' else None
            )
            
            # Заполняем таблицу
            current_date = datetime.now().date()
            
            for item in items:
                try:
                    status = item[5] if len(item) > 5 else ''
                    deadline = item[7] if len(item) > 7 else None
                    
                    row_tags = []
                    if deadline and status not in ['completed', 'on_hold']:
                        try:
                            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                            if deadline_date < current_date:
                                row_tags.append('overdue')
                            else:
                                row_tags.append(status)
                        except:
                            row_tags.append(status)
                    else:
                        row_tags.append(status)
                    
                    self.tree.insert('', tk.END, values=item[:9], tags=row_tags)
                except:
                    continue
            
            self.update_status(f"Найдено записей: {len(items)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске:\n{str(e)}")
        
    def reset_filters(self):
        """Сброс фильтров"""
        self.search_var.set("")
        self.status_filter_var.set("all")
        self.category_filter_var.set("all")
        self.load_data()
        
    def filter_by_status(self, status):
        """Фильтрация по статусу"""
        self.status_filter_var.set(status)
        self.search()
        
    def show_all(self):
        """Показать все записи"""
        self.reset_filters()
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        try:
            # Сначала скрываем предыдущее меню
            self.hide_context_menu(event)
            
            # Определяем строку, на которой был клик
            row_id = self.tree.identify_row(event.y)
            if row_id:
                # Выделяем строку
                self.tree.selection_set(row_id)
                
                # Показываем меню
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Ошибка при показе контекстного меню: {e}")
            
    def change_status(self, status):
        """Изменение статуса записи"""
        selected = self.tree.selection()
        if not selected:
            return
            
        try:
            item_id = self.tree.item(selected[0])['values'][0]
            # Получаем текущие данные
            result = db.get_study_item_by_id(item_id)
            if result:
                item, tags = result
            else:
                item, tags = None, []
            
            if item:
                # Обновляем статус
                data = {
                    'title': item[1] if len(item) > 1 else '',
                    'description': item[2] if len(item) > 2 else '',
                    'category_id': item[3] if len(item) > 3 else None,
                    'rating': item[4] if len(item) > 4 else 3,
                    'status': status,
                    'deadline': item[7] if len(item) > 7 else None,
                    'hours_spent': item[8] if len(item) > 8 else 0,
                    'priority': item[9] if len(item) > 9 else 3,
                    'tags': [t[0] for t in tags] if tags else []
                }
                db.update_study_item(item_id, data)
                self.load_data()
                self.update_status(f"Статус изменен на {self.get_status_text(status)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус:\n{str(e)}")
            
    def manage_categories(self):
        """Управление категориями"""
        try:
            dialog = CategoriesDialog(self.root, self.update_category_filter)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть управление категориями:\n{str(e)}")
        
    def manage_tags(self):
        """Управление тегами"""
        try:
            dialog = TagsDialog(self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть управление тегами:\n{str(e)}")
        
    def export_data(self):
        """Экспорт данных"""
        messagebox.showinfo("Информация", "Функция экспорта будет доступна в следующей версии")
        
    def import_data(self):
        """Импорт данных"""
        messagebox.showinfo("Информация", "Функция импорта будет доступна в следующей версии")
        
    def show_statistics(self):
        """Показать окно статистики"""
        try:
            stats = db.get_statistics()
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Статистика")
            stats_window.geometry("400x350")
            stats_window.transient(self.root)
            stats_window.resizable(False, False)
            
            # Центрируем окно
            stats_window.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - stats_window.winfo_width()) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - stats_window.winfo_height()) // 2
            stats_window.geometry(f"+{x}+{y}")
            
            main_frame = ttk.Frame(stats_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            text = f"""
            📊 ОБЩАЯ СТАТИСТИКА
            ===================
            Всего записей: {stats['total']}
            Всего часов: {stats['total_hours']}
            Средний рейтинг: {stats['avg_rating']:.1f}
            Просрочено: {stats['overdue']}
            
            📌 ПО СТАТУСАМ
            ==============
            📅 Запланировано: {stats['by_status'].get('planned', 0)}
            ⚡ В процессе: {stats['by_status'].get('in_progress', 0)}
            ✅ Завершено: {stats['by_status'].get('completed', 0)}
            ⏸ На паузе: {stats['by_status'].get('on_hold', 0)}
            
            📁 ПО КАТЕГОРИЯМ
            ===============
            """
            
            for category, count in stats['by_category'].items():
                text += f"{category}: {count}\n"
            
            label = ttk.Label(main_frame, text=text, justify=tk.LEFT, font=('Courier', 10))
            label.pack(padx=10, pady=10)
            
            ttk.Button(main_frame, text="Закрыть", command=stats_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось показать статистику:\n{str(e)}")
        
    def show_category_progress(self):
        """Показать прогресс по категориям"""
        messagebox.showinfo("Информация", "Функция графиков будет доступна в следующей версии")
        
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()