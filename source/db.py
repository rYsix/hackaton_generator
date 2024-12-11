import pickle
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()

# Модель для пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    embedding = Column(LargeBinary, nullable=False)  # Сериализованные данные эмбеддинга
    photo = Column(LargeBinary, nullable=True)  # Сериализованное изображение в формате numpy array

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

# Модель для заказа
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    for_user = Column(Integer, ForeignKey('users.id'), nullable=False)  # Внешний ключ на таблицу пользователей
    positions = Column(JSON, nullable=False)  # JSON-поле для хранения позиций заказа

    user = relationship("User", back_populates="orders")

class Database:
    def __init__(self, db_url='sqlite:///app.db'):
        self.db_file = db_url.replace('sqlite:///', '')  # Извлекаем имя файла SQLite
        self.engine = create_engine(db_url, echo=False)  # echo=False для отключения логов SQL
        self.Session = sessionmaker(bind=self.engine)

        self._initialize_database()

    def _initialize_database(self):
        """Проверяет наличие базы данных и создаёт таблицы, если нужно."""
        inspector = inspect(self.engine)
        if not inspector.has_table(User.__tablename__) or not inspector.has_table(Order.__tablename__):
            print("[LOG DB] Таблицы не найдены. Создаём базу данных...")
            Base.metadata.create_all(self.engine)
            print("[LOG DB] База данных и таблицы успешно созданы.")
        else:
            print("[LOG DB] Таблицы уже существуют. Инициализация завершена.")

    def add_user(self, username, embedding=None, photo=None):
        if embedding is None:
            raise ValueError("[ОШИБКА DB] Эмбеддинг обязателен для добавления пользователя.")

        serialized_embedding = pickle.dumps(embedding)
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

    def add_order(self, username, positions):
        if not isinstance(positions, dict):
            raise ValueError("[ОШИБКА DB] Позиции заказа должны быть в формате JSON (dict).")

        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                print(f"[LOG DB] Пользователь '{username}' не найден.")
                return False

            order = Order(for_user=user.id, positions=positions)
            session.add(order)
            session.commit()
            print(f"[LOG DB] Заказ для пользователя '{username}' успешно добавлен.")
            return True
        except Exception as e:
            session.rollback()
            print(f"[ОШИБКА DB] Не удалось добавить заказ для пользователя '{username}': {e}")
            return False
        finally:
            session.close()

    def get_all_users(self):
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

    def get_orders_by_user(self, username):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                print(f"[LOG DB] Пользователь '{username}' не найден.")
                return []

            orders = session.query(Order).filter_by(for_user=user.id).all()
            return [{"id": order.id, "positions": order.positions} for order in orders]
        except Exception as e:
            print(f"[ОШИБКА DB] Не удалось получить заказы для пользователя '{username}': {e}")
            return []
        finally:
            session.close()
