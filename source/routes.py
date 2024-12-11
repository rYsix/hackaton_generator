# routes.py
# комменты:
# тут хранится код с блюпринтами
# каждый блюпринт отвечает за свою логику: main_bp, auth_bp, video_bp
# код максимально простой и проверенный
# обрабатываем исключения и выводим ошибки
# блюпринты потом подключаются в основном файле

from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
import time

def create_main_blueprint(web):
    main_bp = Blueprint('main_bp', __name__)

    @main_bp.route('/')
    def index():
        # главная страница
        try:
            web.log("Главная страница загружена.")
            return render_template('index.html')
        except Exception as e:
            web.log(f"Ошибка: {e}")
            flash("Ошибка при загрузке главной страницы.")
            return redirect(url_for('main_bp.index'))
    return main_bp


def create_menu_blueprint(web):
    menu_bp = Blueprint('menu_bp', __name__)

    @menu_bp.route('/menu')
    def menu():
        try:
            if not web.user.is_auth:
                flash("Пожалуйста войдите, перед использованием меню")
                return redirect(url_for('main_bp.index'))
            web.log("Menu страница загружена.")
            return render_template('menu/menu.html', username = web.user.username)
        except Exception as e:
            web.log(f"Ошибка: {e}")
            flash("Ошибка при загрузке menu страницы.")
            return redirect(url_for('main_bp.index'))
        
    @menu_bp.route('/history')
    def history():
        try:
            if not web.user.is_auth:
                flash("Пожалуйста войдите, перед использованием")
                return redirect(url_for('main_bp.index'))
            web.log("Menu - history страница загружена.")
            return render_template('menu/history.html', username = web.user.username)
        except Exception as e:
            web.log(f"Ошибка: {e}")
            flash("Ошибка при загрузке menu history страницы.")
            return redirect(url_for('main_bp.index'))
        
    @menu_bp.route('/online')
    def online():
        try:
            if not web.user.is_auth:
                flash("Пожалуйста войдите, перед использованием")
                return redirect(url_for('main_bp.index'))
            web.log("Menu - online страница загружена.")
            return render_template('menu/online.html', username = web.user.username)
        except Exception as e:
            web.log(f"Ошибка: {e}")
            flash("Ошибка при загрузке menu online страницы.")
            return redirect(url_for('main_bp.index'))

    return menu_bp

def create_auth_blueprint(web):
    auth_bp = Blueprint('auth_bp', __name__)

    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        # логин по лицу
        try:
            if request.method == 'POST':
                frame = web.camera.get_frame(RGB2=True)
                if frame is None:
                    web.log("Нет кадра с камеры.")
                    flash("Нет кадра с камеры.")
                    return redirect(url_for('main_bp.index'))
                
                all_users = web.db.get_all_users()
                if not all_users:
                    web.log("Нет пользователей в БД.")
                    flash("Нет зарегистрированных пользователей.")
                    return redirect(url_for('main_bp.index'))

                if not web.face_auth.detect_face(frame):
                    web.log("Лицо не обнаружено.")
                    flash("Лицо не обнаружено.")
                    return redirect(url_for('main_bp.index'))

                embedding = web.face_auth.get_embedding(frame)
                if embedding is None:
                    web.log("Нет эмбеддинга.")
                    flash("Нет эмбеддинга.")
                    return redirect(url_for('main_bp.index'))

                for u in all_users:
                    if web.face_auth.compare_embeddings(embedding, u["embedding"]) \
                       or web.face_auth.compare_photos(frame, u["photo"]):
                        web.user.login(u["id"],u["username"],[])
                        web.log(f"Успешный вход: {u['username']}")
                        flash(f"Привет, {u['username']}!")
                        return redirect(url_for('menu_bp.menu'))

                web.log("Пользователь не найден.")
                flash("Пользователь не найден.")
                return redirect(url_for('main_bp.index'))
            else:
                time.sleep(1)
            return render_template('login.html')
        except Exception as e:
            web.log(f"Ошибка логина: {e}")
            flash("Ошибка логина.")
            return redirect(url_for('main_bp.index'))

    @auth_bp.route('/register', methods=['GET', 'POST'])
    def register():
        # регистрация нового юзера
        try:
            time.sleep(1)
            if request.method == 'POST':
                username = request.form['username']
                web.log(f"Регистрация: {username}")

                if web.db.get_user_data(username):
                    web.log("Имя занято.")
                    flash("Имя пользователя занято.")
                    return redirect(url_for('main_bp.index'))

                frame = web.camera.get_frame(RGB2=True)
                if frame is None:
                    web.log("Нет кадра.")
                    flash("Нет кадра.")
                    return redirect(url_for('main_bp.index'))

                if not web.face_auth.detect_face(frame):
                    web.log("Лицо не обнаружено.")
                    flash("Лицо не обнаружено.")
                    return redirect(url_for('main_bp.index'))

                embedding = web.face_auth.get_embedding(frame)
                if embedding is None:
                    web.log("Нет эмбеддинга.")
                    flash("Нет эмбеддинга.")
                    return redirect(url_for('main_bp.index'))

                if web.db.add_user(username, embedding=embedding, photo=frame):
                    web.log("Регистрация ок.")
                    flash("Регистрация успешна!")
                    return redirect(url_for('main_bp.index'))
                else:
                    web.log("Проблема при добавлении юзера.")
                    flash("Ошибка регистрации.")
                    return redirect(url_for('main_bp.index'))

            return render_template('register.html')
        except ValueError as e:
            web.log(f"Ошибка регистрации: {e}")
            flash(str(e))
            return redirect(url_for('main_bp.index'))
        except Exception as e:
            web.log(f"Неизвестная ошибка рег: {e}")
            flash("Ошибка, попробуйте позже.")
            return redirect(url_for('main_bp.index'))

    return auth_bp

def create_video_blueprint(web):
    video_bp = Blueprint('video_bp', __name__)

    @video_bp.route('/video_stream')
    def video_stream():
        # видеопоток
        try:
            web.log("Старт видеопотока.")
            return Response(web.camera.generate_video_stream(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        except Exception as e:
            web.log(f"Ошибка видеопотока: {e}")
            flash("Ошибка видеопотока.")
            return redirect(url_for('main_bp.index'))

    return video_bp
