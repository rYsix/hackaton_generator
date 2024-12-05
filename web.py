from flask import Flask, render_template, request, redirect, url_for, Response, flash

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
            return self.render_with_message('index.html')

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Авторизация пользователя."""
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                self.log(f"Попытка авторизации: {username}")
                if self.db.authenticate_user(username, password):
                    self.log(f"Успешная авторизация: {username}")
                    return redirect(url_for('face_scan'))
                else:
                    self.log(f"Неудачная авторизация: {username}")
                    return self.render_with_message('login.html', "Неверное имя пользователя или пароль.", 401)
            return self.render_with_message('login.html')

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            """Регистрация пользователя с использованием камеры."""
            if request.method == 'POST':
                username = request.form['username']

                self.log(f"Попытка регистрации: {username}")

                

                if self.db.get_user_data(username):
                    self.log(f"Ошибка регистрации: {username} уже существует.")
                    return self.render_with_message('register.html', "Ошибка регистрации. Имя пользователя уже занято.", 400)

                try:
                    frame = self.camera.get_frame(RGB2=True)
                    if frame is None:
                        self.log("Не удалось получить кадр с камеры.")
                        return self.render_with_message('register.html', "Не удалось получить кадр с камеры.", 400)

                    if not self.face_auth.detect_face(frame):
                        self.log("Лицо на фотографии не обнаружено.")
                        return self.render_with_message('register.html', "Лицо на фотографии не обнаружено. Убедитесь, что ваше лицо видно.", 400)

                    embedding = self.face_auth.get_embedding(frame)
                    if embedding is None:
                        self.log("Не удалось извлечь эмбеддинг из кадра.")
                        return self.render_with_message('register.html', "Не удалось извлечь эмбеддинг из кадра. Попробуйте снова.", 400)

                    if self.db.add_user(username, embedding=embedding, photo=frame):
                        self.log(f"Успешная регистрация: {username}")
                        return redirect(url_for('index'))
                    else:
                        self.log(f"Ошибка регистрации: {username} уже существует.")
                        return self.render_with_message('register.html', "Ошибка регистрации. Имя пользователя уже занято.", 400)

                except ValueError as e:
                    self.log(f"Ошибка регистрации: {e}")
                    return self.render_with_message('register.html', str(e), 400)

                except Exception as e:
                    self.log(f"Неизвестная ошибка: {e}")
                    return self.render_with_message('register.html', "Произошла ошибка. Попробуйте позже.", 500)

            return self.render_with_message('register.html')



        @self.app.route('/face_scan')
        def face_scan():
            """Показ потока с камеры."""
            self.log("Страница сканирования лица загружена.")
            return self.render_with_message('face_scan.html')

        @self.app.route('/video_stream')
        def video_stream():
            """Генерация видеопотока с камеры."""
            self.log("Генерация видеопотока началась.")
            return Response(self.camera.generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/authenticate_face', methods=['POST'])
        def authenticate_face():
            """Авторизация с помощью распознавания лица."""
            image_path = request.files['face_image'].filename
            self.log(f"Получено изображение для авторизации: {image_path}")

            embedding = self.face_auth.get_embedding(image_path)

            if embedding is None:
                self.log(f"Не удалось обработать изображение: {image_path}")
                return self.render_with_message('face_scan.html', "Ошибка обработки изображения.", 400)

            user_embedding = self.db.get_user_embedding(request.form['username'])

            if not user_embedding:
                self.log(f"Эмбеддинг пользователя не найден: {request.form['username']}")
                return self.render_with_message('face_scan.html', "Эмбеддинг пользователя не найден.", 404)

            if self.face_auth.compare_embeddings(embedding, user_embedding):
                self.log(f"Успешная аутентификация лица для пользователя: {request.form['username']}")
                return self.render_with_message('face_scan.html', "Аутентификация лица успешна!", 200)
            else:
                self.log(f"Аутентификация лица неудачна для пользователя: {request.form['username']}")
                return self.render_with_message('face_scan.html', "Аутентификация лица не удалась.", 401)

    def run(self):
        """Запуск Flask-приложения."""
        self.log("Запуск Flask-сервера...")
        self.app.run(host='0.0.0.0', port=5000, debug=True)
