from web import Web
from db import Database
from camera import Camera
from face_auth import FaceAuth
from account import Account

def main():
    """Основной запуск программы."""
    print("[ЛОГ MAIN] Запуск основного модуля...")

    try:
        print("[ЛОГ MAIN] Инициализация базы данных...")
        db = Database()
        print("[ЛОГ MAIN] База данных успешно инициализирована.")
    except Exception as e:
        print(f"[ERROR MAIN] ERROR при инициализации базы данных: {e}")
        return

    try:
        print("[ЛОГ MAIN] Инициализация камеры...")
        camera = Camera()
        print("[ЛОГ MAIN] Камера успешно инициализирована.")
    except Exception as e:
        print(f"[ERROR MAIN] ERROR при инициализации камеры: {e}")
        return

    try:
        print("[ЛОГ MAIN] Инициализация FaceAuth...")
        face_auth = FaceAuth()
        print("[ЛОГ MAIN] FaceAuth успешно инициализирован.")
    except Exception as e:
        print(f"[ERROR MAIN] ERROR при инициализации FaceAuth: {e}")
        return

    try:
        print("[ЛОГ MAIN] Инициализация пользователя...")
        user = Account()
    except Exception as e:
        print(f"[ERROR MAIN] ERROR при инициализации пользователя: {e}")
        return

    try:
        print("[ЛОГ MAIN] Создание и запуск веб-сервера...")
        web = Web(db, camera, face_auth, user)
        print("[ЛОГ MAIN] Веб-сервер успешно создан.")
        web.run()
    except Exception as e:
        print(f"[ERROR MAIN] ERROR при запуске веб-сервера: {e}")
        return

if __name__ == "__main__":
    main()
