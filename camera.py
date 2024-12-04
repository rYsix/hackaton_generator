import cv2

class Camera:
    def __init__(self):
        """Инициализация класса камеры."""
        self.cap = None
        print("[LOG CAMERA] Класс камеры успешно создан.")

    def start(self):
        """Инициализация камеры."""
        print("[LOG CAMERA] Инициализация камеры...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("[ERROR CAMERA] Не удалось инициализировать камеру. Проверьте подключение.")
        print("[LOG CAMERA] Камера успешно инициализирована.")

    def get_frame(self, RGB2=False):
        """Получение текущего кадра с камеры."""
        if not self.cap:
            raise RuntimeError("[ERROR CAMERA] Камера не инициализирована. Вызовите метод start().")
        
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("[ERROR CAMERA] Не удалось получить кадр с камеры. Попробуйте снова.")
        
        if RGB2:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return frame

    def stop(self):
        """Остановка работы с камерой."""
        if self.cap:
            print("[LOG CAMERA] Завершение работы с камерой...")
            self.cap.release()
            self.cap = None
            print("[LOG CAMERA] Работа с камерой завершена.")

    def generate_video_stream(self):
        """Генератор видеопотока в формате MJPEG."""
        try:
            print("[LOG CAMERA] Запуск видеопотока...")
            self.start()
            frame_count = 0  # Счётчик кадров для логирования
            while True:
                frame = self.get_frame()
                frame_count += 1
                if frame_count % 60 == 0:  # Логировать каждые 60 кадров
                    print(f"[LOG CAMERA] Обработано {frame_count} кадров.")
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[ERROR CAMERA] Ошибка во время видеопотока: {e}")
        finally:
            self.stop()
            print("[LOG CAMERA] Видеопоток завершён.")
