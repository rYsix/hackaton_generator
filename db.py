import pickle
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Модель для пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    embedding = Column(LargeBinary, nullable=False)  # Сериализованные данные эмбеддинга
    photo = Column(LargeBinary, nullable=True)  # Сериализованное изображение в формате numpy array


class Database:
    def __init__(self, db_url='sqlite:///app.db'):
        self.db_file = db_url.replace('sqlite:///', '')  # Извлекаем имя файла SQLite
        self.engine = create_engine(db_url, echo=False)  # echo=False для отключения логов SQL
        self.Session = sessionmaker(bind=self.engine)

        self._initialize_database()

    def _initialize_database(self):
        """Проверяет наличие базы данных и создаёт таблицы, если нужно."""
        inspector = inspect(self.engine)
        if not inspector.has_table(User.__tablename__):
            print("[LOG DB] Таблицы не найдены. Создаём базу данных...")
            Base.metadata.create_all(self.engine)
            print("[LOG DB] База данных и таблицы успешно созданы.")
        else:
            print("[LOG DB] Таблицы уже существуют. Инициализация завершена.")

    def add_user(self, username, embedding=None, photo=None):
        """
        Добавление нового пользователя с фото.
        Аргументы:
            username (str): Имя пользователя.
            embedding (list/array): Эмбеддинг лица.
            photo (numpy.ndarray): Фото пользователя в формате numpy array.
        """
        if embedding is None:
            raise ValueError("[ОШИБКА DB] Эмбеддинг обязателен для добавления пользователя.")

        # Сериализация эмбеддинга
        serialized_embedding = pickle.dumps(embedding)

        # Сериализация фото
        serialized_photo = pickle.dumps(photo) if photo is not None else None

        session = self.Session()
        try:
            user = User(username=username, embedding=serialized_embedding, photo=serialized_photo)
            session.add(user)
            session.commit()
            print(f"[LOG DB] Пользователь '{username}' успешно добавлен.")
        except Exception as e:
            session.rollback()
            print(f"[ОШИБКА DB] Не удалось добавить пользователя '{username}': {e}")
            return False
        finally:
            session.close()
        return True

    def get_user_data(self, username):
        """
        Получение данных пользователя.
        Аргументы:
            username (str): Имя пользователя.
        Возвращает:
            dict: Содержит username, десериализованный эмбеддинг и фото (numpy array).
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                embedding = pickle.loads(user.embedding) if user.embedding else None
                photo = pickle.loads(user.photo) if user.photo else None
                return {"username": user.username, "embedding": embedding, "photo": photo}
            else:
                print(f"[LOG DB] Пользователь '{username}' не найден.")
                return None
        except Exception as e:
            print(f"[ОШИБКА DB] Не удалось получить данные пользователя '{username}': {e}")
        finally:
            session.close()

    def get_all_users(self):
        """
        Возвращает всех пользователей в виде списка словарей.
        Возвращает:
            list[dict]: Список пользователей с их данными.
        """
        session = self.Session()
        try:
            users = session.query(User).all()
            user_data_list = []
            for user in users:
                user_data_list.append({
                    "id": user.id,
                    "username": user.username,
                    "embedding": pickle.loads(user.embedding) if user.embedding else None,
                    "photo": pickle.loads(user.photo) if user.photo else None
                })
            return user_data_list
        except Exception as e:
            print(f"[ОШИБКА DB] Не удалось получить список пользователей: {e}")
            return []
        finally:
            session.close()

    def delete_user(self, username):
        """
        Удаление пользователя по имени.
        Аргументы:
            username (str): Имя пользователя.
        Возвращает:
            bool: True, если пользователь успешно удалён, иначе False.
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                print(f"[LOG DB] Пользователь '{username}' не найден.")
                return False
            session.delete(user)
            session.commit()
            print(f"[LOG DB] Пользователь '{username}' успешно удалён.")
            return True
        except Exception as e:
            session.rollback()
            print(f"[ОШИБКА DB] Не удалось удалить пользователя '{username}': {e}")
            return False
        finally:
            session.close()
