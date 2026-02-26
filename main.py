import tkinter as tk
import database as db
from gui.main_window import MainWindow


def main():
    try:
        print("Инициализация базы данных...")
        db.init_database()
        print("База данных готова")

        print("Запуск приложения...")
        app = MainWindow()
        app.run()

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror(
            "Ошибка запуска",
            f"Не удалось запустить приложение:\n{str(e)}\n\n"
            "Проверьте наличие необходимых библиотек и прав доступа."
        )


if __name__ == "__main__":
    main()
