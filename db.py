import pickle
from sqlalchemy import create_engine, Column, Integer, String, inspect, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

# Модель для пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Пароль должен быть захеширован
    embedding = Column(LargeBinary, nullable=False)  # Сериализованные данные эмбеддинга


class Database:
    def __init__(self, db_url='sqlite:///app.db'):
        self.db_file = db_url.replace('sqlite:///', '')  # Извлекаем имя файла SQLite
        self.engine = create_engine(db_url, echo=False)  # echo=False для отключения логов SQL
        self.Session = sessionmaker(bind=self.engine)

        self._initialize_database()

    def _initialize_database(self):
        """Проверяет наличие файла базы данных и создаёт таблицы, если нужно."""
        if not os.path.exists(self.db_file):
            print("[LOG DB] Файл базы данных не найден. Создаём новую базу данных...")
            self._create_database()
        else:
            print("[LOG DB] Файл базы данных найден. Проверяем таблицы...")
            self._check_and_create_tables()

    def _create_database(self):
        """Создаёт файл базы данных и все таблицы."""
        Base.metadata.create_all(self.engine)
        print("[LOG DB] База данных и таблицы успешно созданы.")

    def _check_and_create_tables(self):
        """Проверяет наличие таблиц и создаёт недостающие."""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        expected_tables = Base.metadata.tables.keys()

        for table in expected_tables:
            if table not in existing_tables:
                print(f"[LOG DB] Таблица '{table}' не найдена. Создаём...")
                Base.metadata.tables[table].create(self.engine)
            else:
                print(f"[LOG DB] Таблица '{table}' существует.")

    def add_user(self, username, password, embedding=None):
        """Добавление нового пользователя."""
        if embedding is None:
            raise ValueError("[ОШИБКА DB] Эмбеддинг обязателен для добавления пользователя.")

        # Сериализация эмбеддинга
        serialized_embedding = pickle.dumps(embedding)

        session = self.Session()
        try:
            user = User(username=username, password=password, embedding=serialized_embedding)
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

    def get_user_embedding(self, username):
        """Получение эмбеддинга пользователя."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user and user.embedding:
                # Десериализация эмбеддинга
                return pickle.loads(user.embedding)
            else:
                print(f"[LOG DB] Эмбеддинг для пользователя '{username}' не найден.")
                return None
        except Exception as e:
            print(f"[ОШИБКА DB] Не удалось получить эмбеддинг для пользователя '{username}': {e}")
        finally:
            session.close()
        return None

    def update_user_embedding(self, username, embedding):
        """Обновление эмбеддинга пользователя."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                # Сериализация эмбеддинга
                serialized_embedding = pickle.dumps(embedding)
                user.embedding = serialized_embedding
                session.commit()
                print(f"[LOG DB] Эмбеддинг пользователя '{username}' успешно обновлён.")
                return True
            else:
                print(f"[LOG DB] Пользователь '{username}' не найден.")
                return False
        except Exception as e:
            session.rollback()
            print(f"[ОШИБКА DB] Не удалось обновить эмбеддинг для пользователя '{username}': {e}")
        finally:
            session.close()
        return False
