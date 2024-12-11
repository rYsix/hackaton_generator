# web.py (или app.py)
# комменты:
# основной файл с классом Web
# импортируем блюпринты из routes.py и регаем их
# не ломаем старый код, просто убираем маршруты внутрь блюпринтов

from flask import Flask, flash
import time
from routes import create_main_blueprint, create_auth_blueprint, create_video_blueprint,  create_menu_blueprint

class Web:
    def __init__(self, db, camera, face_auth, user):
        self.app = Flask(__name__)
        self.app.secret_key = 'supersecretkey'
        self.db = db
        self.user = user
        self.camera = camera
        self.face_auth = face_auth

        self.app.register_blueprint(create_main_blueprint(self))
        self.app.register_blueprint(create_menu_blueprint(self), url_prefix='/menu')
        self.app.register_blueprint(create_auth_blueprint(self), url_prefix='/auth')
        self.app.register_blueprint(create_video_blueprint(self), url_prefix='/video')

    def log(self, message):
        print(f"[LOG WEB] {message}")

    def run(self):
        self.log("Запуск Flask-сервера...")
        self.app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
