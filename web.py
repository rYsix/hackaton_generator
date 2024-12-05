from flask import Flask, render_template, request, redirect, url_for, Response, flash
import time

class Web:
    def __init__(self, db, camera, face_auth):
        self.app = Flask(__name__)
        self.app.secret_key = 'supersecretkey'  # Для flash-сообщений
        self.db = db
        self.camera = camera
        self.face_auth = face_auth
        self.setup_routes()

    def log(self, message):
        """Логирует сообщение в консоль с префиксом [LOG WEB]."""
        print(f"[LOG WEB] {message}")

    def render_with_message(self, template, message=None, status_code=200):
        """
        Рендеринг шаблона с выводом сообщения.
        Если message указан, он добавляется в flash.
        """
        if message:
            flash(message)
        return render_template(template), status_code

    def setup_routes(self):
        @self.app.route('/')
        def index():
            """Главная страница с кнопками."""
            self.log("Главная страница загружена.")
            return render_template('index.html')  # Главная страница без редиректов

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Авторизация пользователя через распознавание лица."""
            if request.method == 'POST':
                # Получаем кадр с камеры
                frame = self.camera.get_frame(RGB2=True)
                if frame is None:
                    self.log("Не удалось получить кадр с камеры.")
                    flash("Не удалось получить кадр с камеры.")
                    return redirect(url_for('index'))
                
                # Проверяем наличие лица на кадре
                if not self.face_auth.detect_face(frame):
                    self.log("Лицо на фотографии не обнаружено.")
                    flash("Лицо на фотографии не обнаружено. Убедитесь, что ваше лицо видно.")
                    return redirect(url_for('index'))
                
                # Извлекаем эмбеддинг лица
                embedding = self.face_auth.get_embedding(frame)
                if embedding is None:
                    self.log("Не удалось извлечь эмбеддинг из кадра.")
                    flash("Не удалось извлечь эмбеддинг из кадра. Попробуйте снова.")
                    return redirect(url_for('index'))

                # Получаем список всех пользователей
                all_users = self.db.get_all_users()
                if not all_users:
                    self.log("В базе данных нет зарегистрированных пользователей.")
                    flash("Нет зарегистрированных пользователей.")
                    return redirect(url_for('index'))

                # Проверяем эмбеддинги и фотографии пользователей
                for user in all_users:
                    if self.face_auth.compare_embeddings(embedding, user["embedding"]):
                        self.log(f"Успешная авторизация по эмбеддингу: {user['username']}")
                        flash(f"Добро пожаловать, {user['username']}!")
                        return redirect(url_for('index'))
                    elif self.face_auth.compare_photos(frame, user["photo"]):
                        self.log(f"Успешная авторизация по фотографии: {user['username']}")
                        flash(f"Добро пожаловать, {user['username']}!")
                        return redirect(url_for('index'))

                # Если совпадений не найдено
                self.log("Пользователь не найден.")
                flash("Пользователь не найден. Попробуйте снова.")
                return redirect(url_for('index'))
            else:
                time.sleep(1)
            return render_template('login.html')  # Отображается только при GET-запросе

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            time.sleep(1)
            """Регистрация пользователя с использованием камеры."""
            if request.method == 'POST':
                username = request.form['username']
                self.log(f"Попытка регистрации: {username}")

                if self.db.get_user_data(username):
                    self.log(f"Ошибка регистрации: {username} уже существует.")
                    flash("Имя пользователя уже занято.")
                    return redirect(url_for('index'))  # Возвращаемся на главную страницу

                try:
                    frame = self.camera.get_frame(RGB2=True)
                    if frame is None:
                        self.log("Не удалось получить кадр с камеры.")
                        flash("Не удалось получить кадр с камеры.")
                        return redirect(url_for('index'))

                    if not self.face_auth.detect_face(frame):
                        self.log("Лицо на фотографии не обнаружено.")
                        flash("Лицо на фотографии не обнаружено. Убедитесь, что ваше лицо видно.")
                        return redirect(url_for('index'))

                    embedding = self.face_auth.get_embedding(frame)
                    if embedding is None:
                        self.log("Не удалось извлечь эмбеддинг из кадра.")
                        flash("Не удалось извлечь эмбеддинг из кадра. Попробуйте снова.")
                        return redirect(url_for('index'))

                    if self.db.add_user(username, embedding=embedding, photo=frame):
                        self.log(f"Успешная регистрация: {username}")
                        flash("Регистрация успешна!")
                        return redirect(url_for('index'))
                    else:
                        self.log(f"Ошибка регистрации: {username} уже существует.")
                        flash("Ошибка регистрации. Имя пользователя уже занято.")
                        return redirect(url_for('index'))

                except ValueError as e:
                    self.log(f"Ошибка регистрации: {e}")
                    flash(str(e))
                    return redirect(url_for('index'))

                except Exception as e:
                    self.log(f"Неизвестная ошибка: {e}")
                    flash("Произошла ошибка. Попробуйте позже.")
                    return redirect(url_for('index'))

            return render_template('register.html')  # Отображается только при GET-запросе

        @self.app.route('/video_stream')
        def video_stream():
            """Генерация видеопотока с камеры."""
            self.log("Генерация видеопотока началась.")
            return Response(
                self.camera.generate_video_stream(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

    def run(self):
        """Запуск Flask-приложения."""
        self.log("Запуск Flask-сервера...")
        self.app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
