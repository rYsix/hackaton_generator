import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import time

class Camera:
    def __init__(self, min_interval=1.0):
        """
        Инициализация класса камеры.
        
        Аргументы:
            min_interval (float): Минимальный интервал времени (в секундах) между операциями start/stop.
        """
        self.cap = None
        self.is_running = False
        self.last_operation_time = 0
        self.min_interval = min_interval
        self.last_frame = None  # Кэш последнего кадра
        print("[LOG CAMERA] Класс камеры успешно создан.")

    def _can_operate(self):
        """Проверяет, прошло ли достаточно времени с последней операции."""
        current_time = time.time()
        if current_time - self.last_operation_time < self.min_interval:
            print("[LOG CAMERA] Операция слишком частая. Подождите немного.")
            return False
        self.last_operation_time = current_time
        return True

    def start(self):
        """Инициализация камеры."""
        if self.is_running:
            print("[LOG CAMERA] Камера уже запущена.")
            return
        if not self._can_operate():
            print("[LOG CAMERA] Не удалось запустить камеру из-за частых операций.")
            return

        print("[LOG CAMERA] Инициализация камеры...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("[LOG CAMERA] Не удалось инициализировать камеру. Проверьте подключение.")
            raise RuntimeError("Не удалось инициализировать камеру. Проверьте подключение.")
        self.is_running = True
        print("[LOG CAMERA] Камера успешно инициализирована.")

    def get_frame(self, RGB2=False):
        """
        Получение текущего кадра с камеры.
        
        Возвращает:
            numpy.ndarray: Кадр с камеры в формате (высота, ширина, 3).
        """

        if not self.is_running:
            print("[LOG CAMERA] Камера не запущена. Попытка запустить...")
            try:
                time.sleep()
                self.start()
            except RuntimeError as e:
                print(f"[LOG CAMERA] Не удалось запустить камеру: {e}")
                if self.last_frame is not None:
                    print("[LOG CAMERA] Возвращается последний успешный кадр.")
                    return self.last_frame
                else:
                    raise RuntimeError("Камера не запущена и нет доступных кадров.")

        ret, frame = self.cap.read()
        if not ret:
            print("[LOG CAMERA] Не удалось получить кадр с камеры. Возвращается последний кадр.")
            if self.last_frame is not None:
                return self.last_frame
            else:
                raise RuntimeError("Не удалось получить кадр с камеры и нет доступных кадров.")

        self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if RGB2 else frame
        return self.last_frame

    def stop(self):
        """Остановка работы с камерой."""
        if not self.is_running:
            print("[LOG CAMERA] Камера уже остановлена.")
            return
        if not self._can_operate():
            print("[LOG CAMERA] Не удалось остановить камеру из-за частых операций.")
            return

        print("[LOG CAMERA] Завершение работы с камерой...")
        self.cap.release()
        self.cap = None
        self.is_running = False
        print("[LOG CAMERA] Работа с камерой завершена.")

    def file_to_numpy(self, filepath):
        """
        Преобразует изображение из файла в numpy array.
        
        Аргументы:
            filepath (str): Путь к файлу изображения.
        
        Возвращает:
            numpy.ndarray: Изображение в формате массива пикселей.
        """
        image = cv2.imread(filepath)
        if image is None:
            print(f"[LOG CAMERA] Не удалось загрузить изображение из файла: {filepath}")
            raise ValueError(f"Не удалось загрузить изображение из файла: {filepath}")
        converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print(f"[LOG CAMERA] Изображение из файла {filepath} успешно преобразовано в numpy array.")
        return converted_image

    def bytes_to_numpy(self, byte_data):
        """
        Преобразует изображение из байтов в numpy array.
        
        Аргументы:
            byte_data (bytes): Байты изображения.
        
        Возвращает:
            numpy.ndarray: Изображение в формате массива пикселей.
        """
        try:
            image = Image.open(BytesIO(byte_data))
            converted_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            print("[LOG CAMERA] Байты изображения успешно преобразованы в numpy array.")
            return converted_image
        except Exception as e:
            print(f"[LOG CAMERA] Ошибка при преобразовании байтов в изображение: {e}")
            raise ValueError(f"Ошибка при преобразовании байтов в изображение: {e}")

    def generate_video_stream(self):
        """
        Генератор видеопотока в формате MJPEG.
        
        Возвращает:
            generator[bytes]: Генератор, возвращающий кадры в формате MJPEG (байты JPEG).
        """
        try:
            print("[LOG CAMERA] Запуск видеопотока...")
            self.start()
            frame_count = 0  # Счётчик кадров для логирования
            while self.is_running:
                frame = self.get_frame()
                frame_count += 1
                if frame_count % 60 == 0:  # Логировать каждые 60 кадров
                    print(f"[LOG CAMERA] Обработано {frame_count} кадров.")
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("[LOG CAMERA] Не удалось закодировать кадр в JPEG.")
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[LOG CAMERA] Ошибка во время видеопотока: {e}")
        finally:
            self.stop()
            print("[LOG CAMERA] Видеопоток завершён.")
