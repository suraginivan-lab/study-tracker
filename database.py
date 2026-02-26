import sqlite3

DB_NAME = "study_tracker.db"


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    return conn


def create_main_table(conn):
    """Создание основной таблицы учебных материалов"""
    sql = '''
    CREATE TABLE IF NOT EXISTS study_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        status TEXT DEFAULT 'planned' CHECK(status IN ('planned', 'in_progress', 'completed', 'on_hold')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deadline DATE,
        hours_spent REAL DEFAULT 0,
        priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
    )
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка создания основной таблицы: {e}")


def create_categories_table(conn):
    """Создание таблицы категорий"""
    sql = '''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        color TEXT DEFAULT '#3498db',
        is_default BOOLEAN DEFAULT 0
    )
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка создания таблицы категорий: {e}")


def create_tags_table(conn):
    """Создание таблицы тегов"""
    sql = '''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        color TEXT DEFAULT '#2ecc71'
    )
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка создания таблицы тегов: {e}")


def create_record_tags_table(conn):
    """Создание таблицы связи многие-ко-многим"""
    sql = '''
    CREATE TABLE IF NOT EXISTS study_item_tags (
        study_item_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (study_item_id, tag_id),
        FOREIGN KEY (study_item_id) REFERENCES study_items (id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    )
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка создания таблицы связей: {e}")


def create_study_sessions_table(conn):
    """Таблица для отслеживания учебных сессий"""
    sql = '''
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_item_id INTEGER,
        date DATE DEFAULT CURRENT_DATE,
        duration_minutes INTEGER,
        notes TEXT,
        FOREIGN KEY (study_item_id) REFERENCES study_items (id) ON DELETE CASCADE
    )
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка создания таблицы сессий: {e}")


def init_database():
    """Инициализация базы данных"""
    conn = create_connection()
    if conn:
        create_main_table(conn)
        create_categories_table(conn)
        create_tags_table(conn)
        create_record_tags_table(conn)
        create_study_sessions_table(conn)
        add_default_data(conn)
        conn.close()
        print("База данных успешно инициализирована")


def add_default_data(conn):
    """Добавление тестовых данных"""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('Программирование', 'Курсы по разработке ПО', '#e74c3c', 1),
            ('Математика', 'Высшая математика и алгоритмы', '#3498db', 0),
            ('Иностранные языки', 'Изучение языков', '#2ecc71', 0),
            ('Базы данных', 'SQL и NoSQL', '#f39c12', 0),
            ('Soft skills', 'Личностное развитие', '#9b59b6', 0)
        ]
        cursor.executemany(
            "INSERT INTO categories (name, description, color, is_default) VALUES (?, ?, ?, ?)",
            categories
        )

        tags = [
            ('Python', '#3498db'),
            ('SQL', '#f39c12'),
            ('Важно', '#e74c3c'),
            ('Экзамен', '#9b59b6'),
            ('Курсовая', '#2ecc71'),
            ('Видео', '#1abc9c')
        ]
        cursor.executemany(
            "INSERT INTO tags (name, color) VALUES (?, ?)",
            tags
        )

        study_items = [
            ('Python для начинающих', 'Основы Python',
             1, 5, 'completed', '2024-12-01', 40, 1),
            ('SQL сложные запросы', 'Продвинутые JOIN и подзапросы',
             4, 4, 'in_progress', '2024-12-15', 15, 2),
            ('Английский Intermediate', 'Разговорная практика',
             3, 3, 'in_progress', '2024-12-20', 20, 3),
            ('Дипломный проект', 'Разработка трекера',
             1, 5, 'planned', '2025-01-15', 0, 1),
            ('Алгоритмы сортировки', 'Изучение алгоритмов',
             2, 4, 'planned', '2024-12-10', 0, 2)
        ]
        cursor.executemany(
            """INSERT INTO study_items
               (title, description, category_id, rating, status, deadline, hours_spent, priority)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            study_items
        )

        item_tags = [
            (1, 1), (1, 6),
            (2, 2), (2, 3),
            (4, 3), (4, 5),
        ]
        cursor.executemany(
            "INSERT INTO study_item_tags (study_item_id, tag_id) VALUES (?, ?)",
            item_tags
        )

        conn.commit()
        print("Тестовые данные добавлены")


def add_study_item(data):
    """Добавление нового учебного материала"""
    conn = create_connection()
    cursor = conn.cursor()

    sql = '''
    INSERT INTO study_items
    (title, description, category_id, rating, status, deadline, hours_spent, priority)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(sql, (
        data['title'],
        data['description'],
        data['category_id'],
        data['rating'],
        data['status'],
        data['deadline'],
        data.get('hours_spent', 0),
        data['priority']
    ))
    item_id = cursor.lastrowid

    if data.get('tags'):
        for tag_id in data['tags']:
            cursor.execute(
                "INSERT INTO study_item_tags (study_item_id, tag_id) VALUES (?, ?)",
                (item_id, tag_id)
            )

    conn.commit()
    conn.close()
    return item_id


def get_all_study_items():
    """Получение всех учебных материалов с информацией о категориях и тегах"""
    conn = create_connection()
    cursor = conn.cursor()

    sql = '''
    SELECT
        si.*,
        c.name as category_name,
        c.color as category_color,
        GROUP_CONCAT(t.name, ', ') as tags
    FROM study_items si
    LEFT JOIN categories c ON si.category_id = c.id
    LEFT JOIN study_item_tags sit ON si.id = sit.study_item_id
    LEFT JOIN tags t ON sit.tag_id = t.id
    GROUP BY si.id
    ORDER BY
        CASE si.status
            WHEN 'in_progress' THEN 1
            WHEN 'planned' THEN 2
            WHEN 'on_hold' THEN 3
            WHEN 'completed' THEN 4
        END,
        si.deadline ASC
    '''

    cursor.execute(sql)
    items = cursor.fetchall()
    conn.close()
    return items


def get_study_item_by_id(item_id):
    """Получение одного материала по ID"""
    conn = create_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM study_items WHERE id = ?"
    cursor.execute(sql, (item_id,))
    item = cursor.fetchone()

    sql_tags = """
    SELECT t.* FROM tags t
    JOIN study_item_tags sit ON t.id = sit.tag_id
    WHERE sit.study_item_id = ?
    """
    cursor.execute(sql_tags, (item_id,))
    tags = cursor.fetchall()

    conn.close()
    return item, tags


def update_study_item(item_id, data):
    """Обновление учебного материала"""
    conn = create_connection()
    cursor = conn.cursor()

    sql = '''
    UPDATE study_items
    SET title = ?, description = ?, category_id = ?, rating = ?,
        status = ?, deadline = ?, hours_spent = ?, priority = ?
    WHERE id = ?
    '''
    cursor.execute(sql, (
        data['title'],
        data['description'],
        data['category_id'],
        data['rating'],
        data['status'],
        data['deadline'],
        data['hours_spent'],
        data['priority'],
        item_id
    ))

    cursor.execute(
        "DELETE FROM study_item_tags WHERE study_item_id = ?", (item_id,))
    if data.get('tags'):
        for tag_id in data['tags']:
            cursor.execute(
                "INSERT INTO study_item_tags (study_item_id, tag_id) VALUES (?, ?)",
                (item_id, tag_id)
            )

    conn.commit()
    conn.close()


def delete_study_item(item_id):
    """Удаление учебного материала"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def get_all_categories():
    """Получение всех категорий"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()
    return categories


def add_category(name, description, color, is_default=0):
    """Добавление категории"""
    conn = create_connection()
    cursor = conn.cursor()

    if is_default:
        cursor.execute("UPDATE categories SET is_default = 0")

    cursor.execute(
        "INSERT INTO categories (name, description, color, is_default) VALUES (?, ?, ?, ?)",
        (name, description, color, is_default)
    )
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return category_id


def update_category(category_id, name, description, color, is_default):
    """Обновление категории"""
    conn = create_connection()
    cursor = conn.cursor()

    if is_default:
        cursor.execute("UPDATE categories SET is_default = 0")

    cursor.execute(
        "UPDATE categories SET name = ?, description = ?, color = ?, is_default = ? WHERE id = ?",
        (name, description, color, is_default, category_id)
    )
    conn.commit()
    conn.close()


def delete_category(category_id):
    """Удаление категории"""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM study_items WHERE category_id = ?", (category_id,))
    if cursor.fetchone()[0] > 0:
        # Если используется, спрашиваем подтверждение в GUI
        pass

    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()


def get_all_tags():
    """Получение всех тегов"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tags ORDER BY name")
    tags = cursor.fetchall()
    conn.close()
    return tags


def add_tag(name, color):
    """Добавление тега"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tags (name, color) VALUES (?, ?)", (name, color))
    conn.commit()
    tag_id = cursor.lastrowid
    conn.close()
    return tag_id


def update_tag(tag_id, name, color):
    """Обновление тега"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tags SET name = ?, color = ? WHERE id = ?", (name, color, tag_id))
    conn.commit()
    conn.close()


def delete_tag(tag_id):
    """Удаление тега"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    conn.commit()
    conn.close()


def search_study_items(query, status=None, category_id=None, tag_id=None):
    """Поиск учебных материалов с фильтрацией"""
    conn = create_connection()
    cursor = conn.cursor()

    sql = """
    SELECT DISTINCT
        si.*,
        c.name as category_name,
        c.color as category_color,
        GROUP_CONCAT(t.name, ', ') as tags
    FROM study_items si
    LEFT JOIN categories c ON si.category_id = c.id
    LEFT JOIN study_item_tags sit ON si.id = sit.study_item_id
    LEFT JOIN tags t ON sit.tag_id = t.id
    WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (LOWER(si.title) LIKE LOWER(?) OR LOWER(si.description) LIKE LOWER(?))"
        params.extend([f'%{query}%', f'%{query}%'])

    if status:
        sql += " AND si.status = ?"
        params.append(status)

    if category_id:
        sql += " AND si.category_id = ?"
        params.append(category_id)

    if tag_id:
        sql += " AND sit.tag_id = ?"
        params.append(tag_id)

    sql += " GROUP BY si.id ORDER BY si.deadline ASC"

    cursor.execute(sql, params)
    items = cursor.fetchall()
    conn.close()
    return items


def get_statistics():
    """Получение статистики для отчета"""
    conn = create_connection()
    cursor = conn.cursor()
    stats = {}

    # Общее количество
    cursor.execute("SELECT COUNT(*) FROM study_items")
    stats['total'] = cursor.fetchone()[0]

    # По статусам
    cursor.execute("""
        SELECT status, COUNT(*)
        FROM study_items
        GROUP BY status
    """)
    stats['by_status'] = dict(cursor.fetchall())

    # По категориям
    cursor.execute("""
        SELECT c.name, COUNT(*)
        FROM study_items si
        JOIN categories c ON si.category_id = c.id
        GROUP BY c.name
    """)
    stats['by_category'] = dict(cursor.fetchall())

    # Средний рейтинг
    cursor.execute(
        "SELECT AVG(rating) FROM study_items WHERE rating IS NOT NULL")
    stats['avg_rating'] = cursor.fetchone()[0] or 0

    # Всего часов
    cursor.execute("SELECT SUM(hours_spent) FROM study_items")
    stats['total_hours'] = cursor.fetchone()[0] or 0

    # Просроченные задачи
    cursor.execute("""
        SELECT COUNT(*) FROM study_items
        WHERE deadline < DATE('now') AND status != 'completed'
    """)
    stats['overdue'] = cursor.fetchone()[0]

    conn.close()
    return stats
